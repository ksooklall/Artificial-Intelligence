def normalizer(a, b):
    return 1/(a+b)


def two_test_cancer():
    # Quiz 5
    p_prime_c_two_pos = p_pos_cancer * p_pos_cancer * p_cancer
    p_prime_nc_two_pos = p_pos_ncancer * p_pos_ncancer * p_ncancer

    n = normalizer(p_prime_nc_two_pos + p_prime_c_two_pos)

    return n * p_prime_c_two_pos # Expecting ans = 0.1698


def one_pos_one_neg():
    # Quiz 6
    p_prime_c_pos_neg = p_pos_cancer * p_neg_cancer * p_cancer
    p_prime_nc_pos_neg = p_pos_ncancer * p_neg_ncancer * p_ncancer

    n = normalizer(p_prime_c_pos_neg, p_prime_nc_pos_neg)

    return n * p_prime_c_pos_neg


def test_one_pos_given_test_two_pos():
    # Quiz 8
    p_cancer_pos = (p_pos_cancer * p_cancer) / (p_pos_cancer * p_cancer + p_pos_ncancer * p_ncancer)
    p_ncancer_pos = 1 - p_cancer_pos

    p_two_pos_cancer = p_pos_cancer
    p_two_pos_ncancer = p_pos_ncancer

    return p_two_pos_cancer * p_cancer_pos + p_two_pos_ncancer * p_ncancer_pos

if __name__ == '__main__':

    p_cancer = 0.01
    p_ncancer = 1 - p_cancer

    p_pos_cancer = 0.9
    p_neg_cancer = 1 - p_pos_cancer

    p_pos_ncancer = 0.2
    p_neg_ncancer = 1 - p_pos_ncancer


    print(test_one_pos_given_test_two_pos())
    import pdb; pdb.set_trace()