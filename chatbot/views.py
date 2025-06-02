from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .knowledge_base import get_answer
from .models import ChatHistory

# @login_required
def chat(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        question = request.POST.get('question')
        answer = get_answer(question)
        # Save to chat history
        if request.user.is_authenticated:
            ChatHistory.objects.create(
                user=request.user,
                question=question,
                answer=answer
            )
        
        return JsonResponse({'answer': answer})
    
    return render(request, 'chat.html')


@login_required
def chat_history(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            history = ChatHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
            history_data = [{
                'question': item.question,
                'answer': item.answer,
                'created_at': item.created_at.strftime("%Y-%m-%d %H:%M"),
                'sender': 'user' if i % 2 == 0 else 'bot'  # Alternate sender for display
            } for i, item in enumerate(history)]
            
            return JsonResponse({'status': 'success', 'history': history_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)