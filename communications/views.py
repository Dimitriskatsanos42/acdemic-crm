from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message, User

@login_required
def reply_message(request, message_id):
    parent_message = get_object_or_404(Message, id=message_id)

    if request.method == 'POST':
        sender = request.user
        content = request.POST.get('content')

        # Validate content
        if not content:
            messages.error(request, "Reply content is required.")
            return redirect('message-details', message_id=message_id)

        # Create the reply
        Message.objects.create(
            sender=sender,
            receiver=parent_message.sender if parent_message.sender != request.user else parent_message.receiver,
            content=content,
            reply_to=parent_message
        )
        return redirect('message-details', message_id=message_id)

    return render(request, 'communications/reply_message.html', {
        'parent_message': parent_message
    })

@login_required
def message_detail(request, message_id):
    # Fetch the message
    message = get_object_or_404(Message, id=message_id)

    # Check that the user is authorized to view the message
    if not (message.sender == request.user or message.receiver == request.user):
        return redirect('inbox')

    # Mark the message as read if the user is the receiver
    if message.receiver == request.user and not message.is_read:
        message.is_read = True
        message.save()

    # Traverse the root message to get the conversation
    root_message = message
    while root_message.reply_to:
        root_message = root_message.reply_to

    # Get the entire conversation starting from the root message
    def get_conversation(message):
        history = [message]
        for reply in message.replies.order_by('timestamp'):
            history.extend(get_conversation(reply))
        return history

    conversation = get_conversation(root_message)

    # Render the template
    return render(request, 'communications/message_detail.html', {
        'conversation': conversation,
        'current_message': message
    })

@login_required
def send_message(request):
    if request.method == 'POST':
        sender = request.user
        receiver_email = request.POST.get('receiver')
        content = request.POST.get('content')

        # Check if recipient email exists
        if not receiver_email:
            messages.error(request, "Recipient email is required.")
            return redirect('send-message')

        try:
            receiver = User.objects.get(email=receiver_email)
        except User.DoesNotExist:
            messages.error(request, "Recipient email does not exist.")
            return redirect('send-message')

        # Check if content is provided
        if not content:
            messages.error(request, "Message content is required.")
            return redirect('send-message')

        # Create the message if all checks pass
        Message.objects.create(sender=sender, receiver=receiver, content=content)
        messages.success(request, "Message sent successfully!")
        return redirect('inbox')

    # Render the create message form for GET requests
    return render(request, 'communications/send_message.html')

@login_required
def inbox(request):
    # Fetch all messages where the user is the sender or receiver
    messages_query = Message.objects.filter(
        sender=request.user
    ) | Message.objects.filter(receiver=request.user)

    # Only include root messages (the start of a thread)
    root_messages = messages_query.filter(reply_to__isnull=True).order_by('-timestamp')

    return render(request, 'communications/inbox.html', {'chat_messages': root_messages})