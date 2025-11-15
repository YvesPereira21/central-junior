from django.dispatch import receiver
from django.core.cache import caches
from django.db.models.signals import post_save, post_delete
from articles.models import Article


cache_view = caches['view_cache']

@receiver(post_save, sender=Article)
def implement_points(sender, instance, created, **kwargs):
    clear_article_cache(instance)

    if created:
        profile = instance.author
        profile.reputation_score += 20
        profile.save(update_fields=['reputation_score'])

@receiver(post_delete, sender=Article)
def decrease_points(sender, instance, **kwargs):
    clear_article_cache(instance)
    profile = instance.author
    new_score= profile.reputation_score - 20
    profile.reputation_score = max(0, new_score)
    profile.save(update_fields=['reputation_score'])

def clear_article_cache(article: Article):
    key_list = "list_article"
    cache_view.delete(key_list)

    key = f"article_{article.pk}"
    cache_view.delete(key)
