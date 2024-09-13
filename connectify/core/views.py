from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, Post, Like
from django.utils.text import slugify
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.http import JsonResponse

@login_required
def index(request):
    # Obtine toate postarile si le ordoneaza dupa data crearii (descrescator)
    posts = Post.objects.all().order_by('-created_at')

    if request.method == 'POST':
        content = request.POST.get('content')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if content or image or video:
            # Generam un slug unic pentru postare
            slug = slugify(content[:50])  # Modifica lungimea slug-ului daca este necesar
            original_slug = slug
            counter = 1

            while Post.objects.filter(slug=slug).exists():
                slug = f'{original_slug}-{counter}'
                counter += 1

            try:
                # Cream o postare noua
                post = Post(user=request.user, content=content, slug=slug)
                if image:
                    post.image = image
                if video:
                    post.video = video
                post.save()
                return redirect('index')
            except IntegrityError as e:
                messages.error(request, 'Could not create post. Please try again.')
                return render(request, 'index.html', {'posts': posts, 'user': request.user})

    return render(request, 'index.html', {'posts': posts, 'user': request.user})

@login_required
def profile(request, username):
    # Obtine utilizatorul si profilul sau, apoi toate postarile sale
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    return render(request, 'profile.html', {'user': user, 'profile': profile, 'posts': posts})

@login_required
def edit_profile(request, username):
    # Verificam daca utilizatorul curent are permisiunea de a edita profilul
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return redirect('profile', username=request.user.username)

    profile = user.profile
    if request.method == 'POST':
        date_of_birth = request.POST.get('date_of_birth')
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')

        if date_of_birth:
            profile.date_of_birth = date_of_birth
        if bio:
            profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile', username=request.user.username)

    return render(request, 'edit_profile.html', {'profile': profile})

@login_required
def delete_avatar(request, username):
    # Verificam daca utilizatorul curent are permisiunea de a sterge avatarul
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return redirect('profile', username=request.user.username)

    profile = user.profile
    if profile.avatar:
        profile.avatar.delete()
        profile.avatar = None
        profile.save()
        messages.success(request, 'Profile picture deleted successfully')

    return redirect('edit_profile', username=user.username)

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not (username and email and password1 and password2):
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different username.')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists. Please login instead or use a different email.')
            return render(request, 'signup.html')

        # Cream un nou utilizator si profil
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            profile = Profile.objects.create(user=user, slug=slugify(username))
            if user:
                auth_login(request, user)
                messages.success(request, 'Account created successfully.')
                return redirect('index')
            else:
                messages.error(request, 'Failed to create account. Please try again.')
                return render(request, 'signup.html')
        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return render(request, 'signup.html')

    return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def upload(request):
    return render(request, 'upload.html')

@login_required
def like_post(request, post_id):
    # Obtine postarea si utilizatorul curent
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    # Verificam daca utilizatorul a dat deja like la postare
    like, created = Like.objects.get_or_create(post=post, user=user)

    if not created:
        # Utilizatorul a dat deja like, deci il eliminam
        like.delete()
    else:
        # Utilizatorul a dat like, deci il salvam
        like.save()

    # Redirectionam utilizatorul in functie de locul de unde a venit cererea
    referer = request.META.get('HTTP_REFERER', '/')
    if 'profile' in referer:
        return redirect(referer)
    else:
        return redirect('index')

@login_required
def unlike_post(request, post_id):
    # Obtine postarea si utilizatorul curent
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    try:
        # Eliminam like-ul daca exista
        like = Like.objects.get(user=user, post=post)
        like.delete()
    except Like.DoesNotExist:
        pass
    
    # Redirectionam utilizatorul in functie de locul de unde a venit cererea
    referer = request.META.get('HTTP_REFERER', '/')
    if 'profile' in referer:
        return redirect(referer)
    else:
        return redirect('index')

@login_required
def follow_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_to_follow = get_object_or_404(User, pk=user_id)
        
        profile = request.user.profile
        if not profile.following.filter(pk=user_to_follow.profile.pk).exists():
            profile.following.add(user_to_follow.profile)
            return HttpResponse("User followed successfully")
        else:
            profile.following.remove(user_to_follow.profile)
            return HttpResponse("User unfollowed successfully")

    return HttpResponse("Follow failed")

def unfollow_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_to_unfollow = get_object_or_404(User, pk=user_id)
        
        profile = request.user.profile
        if profile.following.filter(pk=user_to_unfollow.profile.pk).exists():
            profile.following.remove(user_to_unfollow.profile)
            return HttpResponse("User unfollowed successfully")

    return HttpResponse("Unfollow failed")

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Verificam daca utilizatorul curent este autorul postarii
    if request.user == post.user:
        post.delete()
        messages.success(request, 'Post deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this post.')
    
    return redirect('index')

@login_required
def check_follow_status(request):
    if request.method == 'GET' and request.is_ajax():
        user_id = request.GET.get('user_id')
        user_to_check = get_object_or_404(User, pk=user_id)

        profile = request.user.profile
        is_following = profile.following.filter(pk=user_to_check.profile.pk).exists()

        data = {
            'is_following': is_following
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request'})
