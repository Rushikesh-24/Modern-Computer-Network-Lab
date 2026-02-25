import matplotlib.pyplot as plt

def manchester_encode(bit_string, save_path="manchester_signal.png"):
    # Validate input
    if not all(bit in "01" for bit in bit_string):
        raise ValueError("Input must contain only 0s and 1s")

    time = []
    signal = []

    t = 0  # time counter

    for bit in bit_string:
        if bit == '1':
            levels = [-1, 1]
        else:
            levels = [1, -1]
        time.extend([t, t + 0.5])
        signal.extend([levels[0], levels[0]])

        time.extend([t + 0.5, t + 1])
        signal.extend([levels[1], levels[1]])

        t += 1

    # Plot
    print(time, signal)
    plt.figure()
    plt.step(time, signal, where='post')
    plt.ylim(-2, 2)
    plt.yticks([-1, 1])
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.title(f"Manchester Encoding for Data = {bit_string}")
    plt.grid(True)

    plt.savefig(save_path)
    plt.show()

    print(f"Image saved as {save_path}")


while True:
    data = input("\nEnter binary data (or type 'exit' to quit): ")

    if data.lower() == "exit":
        print("Exiting program...")
        break

    try:
        manchester_encode(data)
    except ValueError as e:
        print("Error:", e)