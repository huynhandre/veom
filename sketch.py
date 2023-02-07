
higher_f_limit = 5
lower_f_limit = -2

val1 = 2
val2 = -7
val3 = 8
if all(lower_f_limit < x < higher_f_limit for x in (val1, val2, val3)):
    print("True")
else:
    print("False")