from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save
from credentials.models import Credential
from profiles.models import UserProfile


EXPERIENCE_LEVEL = {'JR': 100, 'PL': 300, 'SR': 500}

@receiver(pre_save, sender=Credential)
def detect_verification_change(sender, instance, **kwargs):
    if instance.pk is None:
        return

    try:
        old_instance = Credential.objects.get(pk=instance.pk)
    except Credential.DoesNotExist:
        return

    if instance.is_verified and not old_instance.is_verified:
        instance._verification_changed_to_true = True
    elif not instance.is_verified and old_instance.is_verified:
        instance._verification_revoked = True

@receiver(post_save, sender=Credential)
def transform_in_professional(sender, instance, created, **kwargs):
    was_just_verified = getattr(instance, '_verification_changed_to_true', False)
    was_just_revoked = getattr(instance, '_verification_revoked', False)
    profile = instance.profile

    if was_just_verified:
        add_points(instance)

        if instance.experience in EXPERIENCE_LEVEL and not profile.is_professional:
            UserProfile.objects.filter(pk=profile.pk).update(is_professional=True)

    elif was_just_revoked:
        remove_points(instance)

        verifiy_quantity_credential = profile.credential_set.filter(
            is_verified=True,
            experience__in=EXPERIENCE_LEVEL.keys()
        ).exclude(pk=instance.pk).count()

        if verifiy_quantity_credential == 0 and profile.is_professional:
            UserProfile.objects.filter(pk=profile.pk).update(is_professional=False)

@receiver(post_delete, sender=Credential)
def change_reputation_by_credential(sender, instance, **kwargs):
    profile = instance.profile
    if instance.is_verified and profile.is_professional:
        remove_points(instance)

        count_quantity = profile.credential_set.filter(
            is_verified=True,
            experience__in=EXPERIENCE_LEVEL.keys()
        ).count()

        if count_quantity == 0 and profile.is_professional:
            UserProfile.objects.filter(pk=profile.pk).update(is_professional=False)

def add_points(credential: Credential):
    profile = credential.profile
    points_to_add = EXPERIENCE_LEVEL.get(credential.experience)
    if points_to_add is None:
        return

    profile.reputation_score += points_to_add
    profile.save(update_fields=['reputation_score'])

def remove_points(credential: Credential):
    profile = credential.profile
    points_to_remove = EXPERIENCE_LEVEL.get(credential.experience)

    if points_to_remove is None:
        return

    new_score = profile.reputation_score - points_to_remove
    profile.reputation_score = max(0, new_score)
    profile.save(update_fields=['reputation_score'])
