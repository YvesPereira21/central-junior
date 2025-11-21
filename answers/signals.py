from django.dispatch import receiver
from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save, post_delete
from answers.models import Answer
from questions.models import Question


cache_view = caches['view_cache']


@receiver(pre_save, sender=Answer)
def verify_answer_has_solution_accepted(sender, instance, **kwargs):
    if instance.pk is None:
        return

    answer = Answer.objects.get(pk=instance.pk)

    if instance.is_accepted and not answer.is_accepted:
        instance._answer_change_to_accepted = True
    if not instance.is_accepted and answer.is_accepted:
        instance._answer_want_be_revoked = True


@receiver(post_save, sender=Answer)
def created_answer(sender, instance, created, **kwargs):
    was_changed_to_accepted = getattr(instance, '_answer_change_to_accepted', False)
    want_be_revoked = getattr(instance, '_answer_want_be_revoked', False)
    clear_question_cache(instance.question.pk)

    if created:
        return

    if was_changed_to_accepted:
        alter_is_solutioned(instance, True)
        get_profile = instance.author
        get_profile.reputation_score += 20
        get_profile.save(update_fields=['reputation_score'])
    elif want_be_revoked:
        return


@receiver(post_delete, sender=Answer)
def decrease_reputation_score(sender, instance, **kwargs):
    if instance.is_accepted:
        author = instance.author
        try:
            alter_is_solutioned(instance, False)
        except ObjectDoesNotExist:
            pass

        new_score = author.reputation_score - 20
        author.reputation_score = max(0, new_score)
        author.save(update_fields=['reputation_score'])

    if instance.question_id:
        clear_question_cache(instance.question_id)


def alter_is_solutioned(answer: Answer, state: bool):
    question = answer.question
    Question.objects.filter(pk=question.pk).update(is_solutioned=state)


def clear_question_cache(question_pk):
    key = f"question_detail_{question_pk}"
    cache_view.delete(key)

    key_list = f"answers_question_list_{question_pk}"
    cache_view.delete(key_list)

    cache_view.delete("list_all_question_published")
