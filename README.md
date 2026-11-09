This standard disclaimer states that the work is entirely fictional and any resemblance to real people, places, or events is coincidental.

DEALERDESK v2.3
===============

Dealer management for the showroom: stock, customers, quotes and invoices.


QUICK START (Linux, macOS, or WSL on Windows)
---------------------------------------------

You need a C compiler (gcc or clang). From the repository root:

    gcc -o dealerdesk *.c -lm
    ./dealerdesk

* Always run it from the repository root. It reads and writes the files in ./data
* Pick a menu option by typing its number and pressing ENTER. 0 goes back, and
  0 on the main menu exits.
* Every change (new vehicle, sale, ...) is saved to data/*.dat immediately.
  To put the sample data back:

      git checkout -- data


BUILD
-----

    gcc -o dealerdesk *.c -lm   (or just: make)

(Windows releases are built with the Borland compiler on the old build PC.)


RUN
---

    ./dealerdesk

Data files are read from the data/ folder, relative to the directory you run
the program from (so run it from the repository root):

    stock.dat       vehicles
    customers.dat   customers
    invoices.dat    invoices
    next_ids.dat    id counters

Do NOT edit the .dat files by hand while the program is running!


MENU
----

    1. Stock
    2. Customers
    3. Quote
    4. Sell vehicle
    5. Invoices
    9. Help
    0. Exit


PRICING RULES
-------------

* Trade customers get a 10% trade discount, taken off the list price.
* Fleet customers get a 4% fleet discount, taken off the list price. A
  customer is either trade or fleet, never both. Mark a customer as fleet
  under Customers, option 4, or answer Y to "Fleet customer" when adding one.
* Salesman discount is a percentage of the list price after the trade or
  fleet discount. It is limited to 0-15%: a higher figure is capped at 15%.
  There is no manager PIN.
* Net price = list price minus the discounts above.
* Delivery (150.00) is added to every sale. VAT (20%) is calculated on the
  net price plus delivery.
* First registration (55.00) is added to every sale and has no VAT.
* Trade-in value is taken off the final total.


RELEASE
-------

See RELEASE.txt


Problems: ask Phil (ext. 214).
