from search.bfs import BFS
from search.dfs import DFS
from search.hybrid import HybridSearch
from solver.kernel_solver import KernelSolver


def main():
    kernel_solver_dfs = KernelSolver(DFS())
    kernel_solver_dfs.executeStrategy()

    kernel_solver_bfs = KernelSolver(BFS())
    kernel_solver_bfs.executeStrategy()

    kernel_solver_hybrid = KernelSolver(HybridSearch())
    kernel_solver_hybrid.executeStrategy()


if __name__ == "__main__":
    main()