from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from articles.models import Article


@receiver(post_save, sender=Article)
def implement_points(sender, instance, created, **kwargs):

    if created:
        profile = instance.author
        profile.reputation_score += 20
        profile.save(update_fields=['reputation_score'])

@receiver(post_delete, sender=Article)
def decrease_points(sender, instance, **kwargs):
    profile = instance.author
    new_score= profile.reputation_score - 20
    profile.reputation_score = max(0, new_score)
    profile.save(update_fields=['reputation_score'])
