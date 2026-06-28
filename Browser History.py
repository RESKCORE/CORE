class Node:
    def __init__(self, url):
        self.url = url
        self.prev = None
        self.next = None


class BrowserHistory:
    def __init__(self):
        self.head = None
        self.current = None

    # Visit a new webpage
    def visit(self, url):
        new_node = Node(url)

        # First webpage
        if self.head is None:
            self.head = new_node
            self.current = new_node
            print(f"Visited: {url}")
            return

        # Remove forward history
        self.current.next = None

        # Attach new page
        new_node.prev = self.current
        self.current.next = new_node
        self.current = new_node

        print(f"Visited: {url}")

    # Move backward
    def back(self):
        if self.current is not None and self.current.prev is not None:
            self.current = self.current.prev
            print("Current Page:", self.current.url)
        else:
            print("No previous page.")

    # Move forward
    def forward(self):
        if self.current is not None and self.current.next is not None:
            self.current = self.current.next
            print("Current Page:", self.current.url)
        else:
            print("No forward page.")

    # Display current page
    def current_page(self):
        if self.current:
            print("Current Page:", self.current.url)
        else:
            print("No page opened.")

    # Display browser history
    def show_history(self):
        temp = self.head
        print("\nBrowser History:")
        while temp:
            if temp == self.current:
                print(f"-> {temp.url} (Current)")
            else:
                print(f"   {temp.url}")
            temp = temp.next

    # Search webpage
    def search(self, url):
        temp = self.head
        while temp:
            if temp.url == url:
                print(f"{url} found in history.")
                return
            temp = temp.next
        print(f"{url} not found.")

    # Clear all history
    def clear_history(self):
        self.head = None
        self.current = None
        print("Browser history cleared.")


# -------------------------
# Main Program
# -------------------------

browser = BrowserHistory()

while True:
    print("\n===== Browser History =====")
    print("1. Visit Website")
    print("2. Back")
    print("3. Forward")
    print("4. Current Page")
    print("5. Show History")
    print("6. Search Website")
    print("7. Clear History")
    print("8. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        url = input("Enter Website URL: ")
        browser.visit(url)

    elif choice == "2":
        browser.back()

    elif choice == "3":
        browser.forward()

    elif choice == "4":
        browser.current_page()

    elif choice == "5":
        browser.show_history()

    elif choice == "6":
        url = input("Enter URL to search: ")
        browser.search(url)

    elif choice == "7":
        browser.clear_history()

    elif choice == "8":
        print("Exiting Browser...")
        break

    else:
        print("Invalid Choice.")
