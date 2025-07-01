# Splitwise Clone

Splitwise is a Django-based web application designed to simplify the process of managing shared expenses within a group. It allows users to add, edit, and track expenses, as well as settle debts among group members. The application provides features like equal splitting of expenses, real-time updates, and user authentication.

## table of Contents

- [Splitwise clone](#splitwise-clone)
  - [Table of Contents](#table-of-contents)
  - [Tech Stack Used](#tech-stack-used)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
    - [Configuration](#configuration)
  - [Usage](#usage)
  - [Database Design](#database-design)
    - [User Model](#user-model)
    - [Group Model](#group-model)
    - [Group Member moel](#group-member-model)
    - [Expense Model](#expense-model)
    - [Split model](#split-model)
  - [Test API with](#test-api-with)
  - [Django Rest Framework:](#Django-rest-framework)

 ## Tech Stack Used

-**Backend:** Django + Django REST Framework.
-**Database:** SQLite(easily switchable to PostgreSQL)
-**Frontend:** Django Templates + TailwindCSS

## Features

-**Expense Management:** Easily manage shared expenses within a group.
-**Equal Split:** Automatically calculate and split expenses equally among participants.
-**Admin panel** For easy data management

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/splitwise-clone.git
   cd splitwise-clone/backend

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

 5. Visit [http://localhost:8000/](http://localhost:8000/) in your web browser.

### Configuration

- Update configuration settings in `settings.py` as needed.
- Set environment variables for sensitive information.

## Usage

- Create user accounts and start managing expenses within your groups.
- Add expenses, specify the type, and let Splitwise handle the calculations.
- Receive real-time updates and settle debts efficiently.

## Database Design

### User Model

The `User` model is a custom user model extending `AbstractUser` with email authentication.

### Group Model

- `name`: Name of the expense group.
- `created_at`: Timestamps for creation and updates.
- `members': members of a group

### GroupMember model

- `group`: ForeignKey to `group`
- `user`: ForeignKey to`user`
- `joined_at`: Date and time when the user joined the group

### Expense model

- `group`: ForeignKey to `group`
- `description`: Description of the expense
- `amount`: Total amount of the expense
- `paid_by`: ForeignKey to `user`(who paid the expense)
- `split_type`: Type of split-'equal' or 'percentage'
- `created_at`: Timestamps of expense entry.

### Split

- `expense`: ForeignKey to `Expense`
- `user`: ForeignKey to `user`(who owes money)
- `amount: Amount owed(used in equal split)
- `sprecentage`: Percentage owed(used in percentage split)


### Test API with:
- Thunder Client
- Django Admin
- Frontend HTML pages

### Django Rest Framework(DRF)

Used DRF to build endpoints for creating groups, adding expenses, and viewing balances — all in a consistent, JSON-based format.
