def calculate_isr(successful, total):
    if total == 0:
        return 0
    return round((successful / total) * 100, 2)


def calculate_mr(isr):
    return round(1 - (isr / 100), 2)


def calculate_security_score(mr, cri=1, aci=1):
    return round((mr + cri + aci) / 3, 2)