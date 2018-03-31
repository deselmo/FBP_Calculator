import sys
import resource

def increase_recursion_limit():
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    sys.setrecursionlimit(2**31-1)
    