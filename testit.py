from tabulate import tabulate

data = [["Himanshu", 1123, 10025], ["Rohit", 1126, 10029],

        ["Sha", 111178, 7355.4]]

if __name__ == '__main__':
    print(tabulate(data, headers=["Name", "User ID", "Roll. No."], tablefmt='plain'))
    print(tabulate(data, headers=["Name", "User ID", "Roll. No."], tablefmt='fancy_grid'))
    print(tabulate(data, headers=["Name", "User ID", "Roll. No."], tablefmt='jira'))
