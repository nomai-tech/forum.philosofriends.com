from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AccountDeletionForm, CommentForm, QuestionForm, SignupForm
from .models import Comment, Question


def question_list(request):
    questions = Question.objects.select_related('author').prefetch_related('comments').order_by('-created_at')
    return render(request, 'questions/question_list.html', {'questions': questions})


def question_detail(request, pk):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('comments__author'),
        pk=pk,
    )
    if question.slug:
        canonical_url = reverse('question_detail_slug', args=[question.slug])
        if request.path != canonical_url:
            return redirect(canonical_url, permanent=True)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            login_next = reverse('question_detail_slug', args=[question.slug])
            return redirect(f'/accounts/login/?next={login_next}')
        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                question=question,
                author=request.user,
                body=form.cleaned_data['body'],
            )
            return redirect('question_detail_slug', slug=question.slug)
    else:
        form = CommentForm()

    comments = list(question.comments.select_related('author').order_by('created_at'))
    comment_map = {}
    for comment in comments:
        comment_map.setdefault(comment.parent_id, []).append(comment)

    def build_comment_tree(parent_id=None):
        nodes = []
        for comment in comment_map.get(parent_id, []):
            comment.children = build_comment_tree(comment.id)
            nodes.append(comment)
        return nodes

    comment_tree = build_comment_tree()
    return render(
        request,
        'questions/question_detail.html',
        {'question': question, 'comments': comment_tree, 'comment_form': form},
    )


def question_detail_slug(request, slug):
    question = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('comments__author'),
        slug=slug,
    )
    return question_detail(request, question.pk)


@login_required
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect('question_detail_slug', slug=question.slug)
    else:
        form = QuestionForm()
    return render(request, 'questions/question_form.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('question_list')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('question_list')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def account_delete(request):
    # Ensure we're only working with the authenticated user
    # This is redundant but provides explicit security guarantee
    user_to_delete = request.user
    
    if request.method == 'POST':
        form = AccountDeletionForm(user_to_delete, request.POST)
        if form.is_valid():
            # Double-check: ensure the form validated against the correct user
            # The form's clean_password already verified the password matches user_to_delete
            if form.user != user_to_delete:
                # This should never happen, but defense-in-depth
                return redirect('question_list')
            
            # Store user ID for final verification
            user_id = user_to_delete.id
            
            # Logout before deleting to avoid session issues
            logout(request)
            
            # Fetch the user by ID to ensure we're deleting the correct user
            # This prevents any potential race conditions or session manipulation
            try:
                user = User.objects.get(id=user_id)
                # Delete the user (this will cascade delete questions and comments)
                user.delete()
            except User.DoesNotExist:
                # User was already deleted (shouldn't happen, but handle gracefully)
                pass
            
            return redirect('question_list')
    else:
        form = AccountDeletionForm(user_to_delete)
    return render(request, 'registration/account_delete.html', {'form': form})
