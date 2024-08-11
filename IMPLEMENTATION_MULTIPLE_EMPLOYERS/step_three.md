## Step 3

1. The `organisation_employer` field (currently a foreign key for `Organisation`) now needs deprecating by removing from `Epilepsy12User`
   
   ```python
   # remove these lines
   organisation_employer = models.ForeignKey(
        "epilepsy12.Organisation", on_delete=models.CASCADE, blank=True, null=True
    )
   ```

2. Once again, make a commit and then push to live. This will trigger `python manage.py makemigrations` and `python manage.py makemigrations migrate`
