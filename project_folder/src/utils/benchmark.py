from time import perf_counter


# Define a decorator function to measure execution time
def time_benchmark(func):
    def wrapper(*args, **kwargs):
        start_time = perf_counter()  # Record the start time
        result = func(*args, **kwargs)  # Execute the original function
        end_time = perf_counter()  # Record the end time
        execution_time = end_time - start_time  # Calculate the execution time
        print(f"{func.__name__} took {execution_time:.6f} seconds to run.")
        return result

    return wrapper
