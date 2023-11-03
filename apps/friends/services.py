from apps.friends.models import FriendRequest, FriendList


def get_friend_request_or_false(sender, receiver):
    try:
        return FriendRequest.objects.get(sender=sender, receiver=receiver, is_active=True)
    except FriendRequest.DoesNotExist:
        return False


def accept_friend_request(friend_request):
    if friend_request.sender == friend_request.receiver:
        raise ValueError(f'{friend_request.sender} не может принять запрос в друзья от самого себя!')

    receiver_friend_list, _ = FriendList.objects.get_or_create(user=friend_request.receiver)
    add_friend(receiver_friend_list, friend_request.sender)

    sender_friend_list, _ = FriendList.objects.get_or_create(user=friend_request.sender)
    add_friend(sender_friend_list, friend_request.receiver)

    friend_request.is_active = False
    friend_request.save()


def add_friend(friend_list, user):
    if user and user not in friend_list.friends.all():
        friend_list.friends.add(user)


def remove_friend(friend_list, user):
    friend_list.friends.remove(user)


def is_mutual_friend(friends, friend):
    return friend in friends


def decline_friend_request(friend_request):
    friend_request.is_active = False
    friend_request.save()


def cancel_friend_request(friend_request):
    friend_request.is_active = False
    friend_request.save()