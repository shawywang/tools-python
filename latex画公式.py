import matplotlib.pyplot as plt


def main():
    plt.figure(figsize=(10, 5))
    plt.text(0.5, 0.5, r'$\dfrac{d}{dx} \left( \dfrac{\ln(1+x)}{x} \right) = \dfrac{ \dfrac{1}{1+x} \cdot x - \ln(1+x) \cdot 1 }{x^2} = \dfrac{ \dfrac{x}{1+x} - \ln(1+x) }{x^2}$',
             fontsize=20, ha='center')
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    main()
# Python 3.8+
