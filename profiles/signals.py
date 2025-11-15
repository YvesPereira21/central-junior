from django.dispatch import receiver
from django.db.models.signals import post_save
from profiles.models import UserProfile


USER_LEVEL = {0: "Iniciante", 500: 'Intermediário', 1000: "Especialista", 2000: "Elite"}

@receiver(post_save, sender=UserProfile)
def change_level_user_profile(sender, instance, created, **kwargs):

    if created:
        return

    user_profile = instance
    level_profile = get_level_for_score(user_profile.reputation_score)
    if level_profile != user_profile.level:
        UserProfile.objects.filter(pk=user_profile.pk).update(level=level_profile)

def get_level_for_score(score):
    for points, level in sorted(USER_LEVEL.items(), reverse=True):
        if score >= points:
            return level

    return USER_LEVEL[0]
