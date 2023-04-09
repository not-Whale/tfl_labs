class Reader:
    def __init__(self, trs='./static/trs.txt', polynomial='./static/poly.txt'):
        self.trs_file_path = trs
        self.polynomial_file_path = polynomial
        self.trs_list = []
        self.polynomial_list = []

    def parse(self):
        with open(self.trs_file_path, 'r') as trs_file:
            self.trs_list = trs_file.readlines()

        with open(self.polynomial_file_path, 'r') as polynomial_file:
            self.polynomial_list = polynomial_file.readlines()

    def get_trs(self):
        return self.trs_list

    def get_polynomial(self):
        return self.polynomial_list
