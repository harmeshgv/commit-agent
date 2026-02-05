MAX_SUBJECT_LEN = 50


def validate_commit(result):
    subject = result["subject"]

    if len(subject) > MAX_SUBJECT_LEN:
        subject = subject[:MAX_SUBJECT_LEN]

    result["subject"] = subject
    return result
