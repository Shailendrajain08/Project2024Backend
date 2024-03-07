from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from mysite.settings import HIRECODER_FEE
from .models import (
    JobProposalV2,
    JobContract,
)
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

User = get_user_model()


@receiver(post_save, sender=JobProposalV2)
def create_contract(sender, instance, created, **kwargs):
   
    if instance.status == "ACCEPTED_BY_CODER":
        job_post = instance.job_post
        try:
            contract = JobContract.objects.get(job_proposal__job_post=job_post, coder_id=instance.user)
            if contract.job_proposal.status == "REJECTED_BY_CODER":
                status_message = f" with status {contract.job_proposal.status}"
            else:
                status_message = f" with status {contract.job_proposal.status}"
            raise DRFValidationError({"message": f"Contract already exists for this user and job post{status_message}."})
        except ObjectDoesNotExist:
            contract = JobContract.objects.create(
                job_proposal=instance,
                client_id=job_post.user,
                coder_id=instance.user,
                name=f"{str(job_post.user)}_{str(instance.user)}_{str(job_post.title)}",
                end_date=None,
                hourly_rate=instance.hourly_rate,
                hirecoder_fee=HIRECODER_FEE
                )
            contract.save()
        except Exception as e:
            raise DRFValidationError({"message": f"Something went wrong while creating the contract. {e}"})

  
    
