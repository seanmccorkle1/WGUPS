class PackageHashTable:

    def __init__(self, capacity=40, linear_coeff=0, quad_coeff=1):

        self.capacity = capacity
        self.slots = [None] * capacity
        self.flags = ["Never used"] * capacity

        self.linear_coeff, self.quad_coeff = linear_coeff, quad_coeff


    # O(N)  | Called once for each package
    def add(self, pkg):
        
        attempts = 0
        index = hash(pkg.package_id)
        
        if pkg.package_id == 40: index = 0

        while attempts < self.capacity:

            if self.flags[index] == "Never used":

                self.slots[index] = pkg
                self.flags[index] = "Used"
                return True

            attempts += 1

            index = hash(pkg.package_id) + self.linear_coeff * attempts + self.quad_coeff * (attempts ** 2)  # quadratic probing formula

            if index ==40: index=0

        self.expand()
        return self.add(pkg)

    # O(N), linear probing
    def get(self, pkg_id):
        curr_id = hash(pkg_id)
        offset = 0

        if pkg_id == 40: curr_id= 0  # adjust for 0-indexing
        jumping_idx = curr_id

        while self.flags[jumping_idx] != "Never used" and offset < len(self.slots):

            slot = self.slots[jumping_idx]

            if slot is not None and slot.package_id == pkg_id:
                return slot   #return the package

            offset += 1
            jumping_idx = hash(pkg_id) + (self.linear_coeff * offset) + (self.quad_coeff * (offset ** 2))

            if jumping_idx == 40: jumping_idx = 0 #  adjust for 0-index

    # O(N)
    def expand(self):

        new_table = PackageHashTable(capacity = self.capacity * 2, linear_coeff = self.linear_coeff, quad_coeff = self.quad_coeff)

        for pkg in self.slots:
            if pkg is not None:
                new_table.add(pkg)

        self.capacity = new_table.capacity
        self.slots, self.flags  = new_table.slots, new_table.flags