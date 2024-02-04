def kernel_black_box(B, alpha):
    # It should find one element of the kernel B_alpha.
    for beta in B:
        if beta != alpha:
            return {beta}
    return set()

def kernel(A, alpha):
    Cut = set()
    stack = []
    kernel_set = {alpha}  # Kernel initialized with alpha

    for s in A:
        if s != alpha:
            stack.append(s)  # Insert s into the stack

    while stack:
        Hn = stack[-1]  # Look at the last element of stack
        B = kernel_black_box(kernel_set, alpha)  # Find one element of the kernel B_alpha
        
        if B and Hn.issubset(B):
            stack.pop()  # Remove the last element of stack
        elif alpha in B and not Hn.issubset(kernel_set):
            kernel_set = kernel_set.union(B)
            for s in B:
                if s not in Hn:
                    stack.append(s)  # Insert Hn U {s} into the top of the stack
        else:
            Cut = Cut.union({Hn})
            stack.pop()  # Remove the last element of stack

    print("The kernel is:", kernel_set)
    return kernel_set