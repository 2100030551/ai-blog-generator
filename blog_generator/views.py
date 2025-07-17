import os
import uuid
import time
import requests
import yt_dlp

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BlogPost
from blog_generator.utils.openai_api import generate_blog_with_openai


@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def generate_blog_view(request):
    if request.method == "POST":
        video_url = request.POST.get("video_url")
        filepath = None

        if not video_url or not video_url.startswith("http"):
            return render(request, "index.html", {"error": "❌ Please enter a valid YouTube video URL."})

        try:
            # Download YouTube audio
            base_filename = str(uuid.uuid4())
            output_template = os.path.join(settings.MEDIA_ROOT, f"{base_filename}.%(ext)s")
            final_mp3_path = os.path.join(settings.MEDIA_ROOT, f"{base_filename}.mp3")

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'Untitled Video')

            if not os.path.exists(final_mp3_path):
                raise FileNotFoundError(f"Audio file not found: {final_mp3_path}")

            filepath = final_mp3_path

            # Load API keys
            ASSEMBLYAI_API_KEY = settings.ASSEMBLYAI_API_KEY
            OPENAI_API_KEY = settings.OPENAI_API_KEY

            if not ASSEMBLYAI_API_KEY or not OPENAI_API_KEY:
                raise Exception("❌ API keys not set. Check your .env file and settings.")

            # Upload audio to AssemblyAI
            headers_assemblyai = {"authorization": ASSEMBLYAI_API_KEY}
            with open(filepath, 'rb') as f:
                upload_res = requests.post(
                    "https://api.assemblyai.com/v2/upload",
                    headers=headers_assemblyai,
                    files={'file': f}
                )

            if upload_res.status_code != 200:
                raise Exception(f"AssemblyAI upload failed: {upload_res.status_code} - {upload_res.text}")

            audio_url = upload_res.json().get('upload_url')
            if not audio_url:
                raise Exception("❌ Failed to retrieve upload URL from AssemblyAI.")

            # Request transcription
            transcript_res = requests.post(
                "https://api.assemblyai.com/v2/transcript",
                json={"audio_url": audio_url},
                headers=headers_assemblyai
            )

            transcript_id = transcript_res.json().get('id')
            if not transcript_id:
                raise Exception("❌ Failed to initiate transcription.")

            transcript = None
            for _ in range(40):
                poll_res = requests.get(
                    f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                    headers=headers_assemblyai
                )
                status = poll_res.json().get('status')
                if status == 'completed':
                    transcript = poll_res.json().get('text')
                    break
                elif status == 'error':
                    raise Exception("❌ Transcription failed.")
                time.sleep(3)

            if not transcript:
                raise Exception("❌ Transcription timed out.")

            # Generate blog content using OpenAI
            blog_text = generate_blog_with_openai(transcript, OPENAI_API_KEY)

            # Save blog post
            blog = BlogPost.objects.create(
                user=request.user,
                title=title,
                video_url=video_url,
                transcript=transcript,
                blog_content=blog_text
            )

            return redirect('blog_detail', id=blog.id)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return render(request, "index.html", {"error": str(e)})

        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

    return render(request, "index.html")


@login_required(login_url='login')
def all_blogs_view(request):
    blogs = BlogPost.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "all-blogs.html", {"blogs": blogs})


@login_required(login_url='login')
def blog_detail_view(request, id):
    # Ensure user can access only their blog posts
    blog = get_object_or_404(BlogPost, id=id, user=request.user)
    return render(request, "blog-details.html", {"blog": blog})


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        repeat_password = request.POST.get("repeatPassword")

        if password != repeat_password:
            return render(request, "registration/signup.html", {"error_message": "Passwords do not match."})

        if User.objects.filter(username=username).exists():
            return render(request, "registration/signup.html", {"error_message": "Username already exists."})

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "✅ Account created. Please log in.")
        return redirect('login')

    return render(request, "registration/signup.html")
