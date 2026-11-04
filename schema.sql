DROP TABLE IF EXISTS borrowings;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- Unified Users Table for Role-Based Access Control
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL, -- In production, we will hash this
    role TEXT NOT NULL CHECK(role IN ('staff', 'student')),
    phone TEXT,
    registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    total_copies INTEGER NOT NULL DEFAULT 1,
    available_copies INTEGER NOT NULL DEFAULT 1,
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE borrowings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL, -- Now points to users table
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status TEXT NOT NULL DEFAULT 'Issued',
    FOREIGN KEY (book_id) REFERENCES books (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert starter accounts to test the login system
-- Password for all is 'password123'
INSERT INTO users (name, email, password, role, phone) VALUES 
('Library Admin', 'admin@library.com', 'password123', 'staff', '555-0000'),
('Alice Smith', 'alice@example.com', 'password123', 'student', '555-0101'),
('Bob Jones', 'bob@example.com', 'password123', 'student', '555-0202');

-- (Keep your 50 books INSERT statement down here)
-- Insert 50 starter books
INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES 
('The Phoenix Project', 'Gene Kim', '9781942788294', 5, 5),
('Linux Pocket Guide', 'Daniel J. Barrett', '9781491927571', 3, 3),
('Clean Code', 'Robert C. Martin', '9780132350884', 4, 4),
('The Pragmatic Programmer', 'Andrew Hunt', '9780135957059', 5, 5),
('Site Reliability Engineering', 'Betsy Beyer', '9781491929124', 2, 2),
('The DevOps Handbook', 'Gene Kim', '9781942788003', 6, 6),
('Accelerate', 'Nicole Forsgren', '9781942788331', 4, 4),
('Continuous Delivery', 'Jez Humble', '9780321601919', 3, 3),
('Kubernetes Up & Running', 'Kelsey Hightower', '9781492046530', 5, 5),
('Docker Deep Dive', 'Nigel Poulton', '9781521822807', 4, 4),
('Terraform: Up & Running', 'Yevgeniy Brikman', '9781492046905', 3, 3),
('Effective DevOps', 'Jennifer Davis', '9781491926307', 2, 2),
('Infrastructure as Code', 'Kief Morris', '9781491924358', 3, 3),
('Building Microservices', 'Sam Newman', '9781491950357', 4, 4),
('Designing Data-Intensive Applications', 'Martin Kleppmann', '9781449373320', 5, 5),
('Pro Git', 'Scott Chacon', '9781484200773', 3, 3),
('Python Crash Course', 'Eric Matthes', '9781593279288', 6, 6),
('Fluent Python', 'Luciano Ramalho', '9781491946008', 3, 3),
('Grokking Algorithms', 'Aditya Bhargava', '9781617292231', 5, 5),
('Introduction to Algorithms', 'Thomas H. Cormen', '9780262033848', 2, 2),
('Head First Design Patterns', 'Eric Freeman', '9780596007126', 4, 4),
('Design Patterns', 'Erich Gamma', '9780201633610', 3, 3),
('Refactoring', 'Martin Fowler', '9780134757599', 4, 4),
('Code Complete', 'Steve McConnell', '9780735619678', 3, 3),
('The Mythical Man-Month', 'Frederick P. Brooks Jr.', '9780201835953', 2, 2),
('Clean Architecture', 'Robert C. Martin', '9780134494166', 4, 4),
('Release It!', 'Michael T. Nygard', '9781680502398', 3, 3),
('The Goal', 'Eliyahu M. Goldratt', '9780884271956', 5, 5),
('Team Topologies', 'Matthew Skelton', '9781942788812', 4, 4),
('Project to Product', 'Mik Kersten', '9781942788393', 3, 3),
('Domain-Driven Design', 'Eric Evans', '9780321125217', 2, 2),
('Implementing Domain-Driven Design', 'Vaughn Vernon', '9780321834577', 3, 3),
('Cracking the Coding Interview', 'Gayle Laakmann McDowell', '9780984782857', 5, 5),
('Programming Pearls', 'Jon Bentley', '9780201657883', 2, 2),
('Working Effectively with Legacy Code', 'Michael Feathers', '9780131177055', 3, 3),
('The Art of Computer Programming', 'Donald E. Knuth', '9780201485417', 1, 1),
('Computer Networks', 'Andrew S. Tanenbaum', '9780132126953', 4, 4),
('TCP/IP Illustrated', 'W. Richard Stevens', '9780201633467', 3, 3),
('UNIX and Linux System Administration Handbook', 'Evi Nemeth', '9780134277554', 4, 4),
('How Linux Works', 'Brian Ward', '9781593275679', 5, 5),
('The Linux Command Line', 'William E. Shotts Jr.', '9781593273897', 6, 6),
('Practical Vim', 'Drew Neil', '9781934356982', 3, 3),
('Mastering Regular Expressions', 'Jeffrey E.F. Friedl', '9780596528126', 2, 2),
('Learning SQL', 'Alan Beaulieu', '9781492040545', 4, 4),
('High Performance MySQL', 'Baron Schwartz', '9781449314286', 3, 3),
('MongoDB: The Definitive Guide', 'Kristina Chodorow', '9781449344689', 2, 2),
('Elasticsearch: The Definitive Guide', 'Clinton Gormley', '9781449358549', 2, 2),
('Kafka: The Definitive Guide', 'Neha Narkhede', '9781491936160', 3, 3),
('Learning React', 'Alex Banks', '9781492051220', 4, 4),
('Eloquent JavaScript', 'Marijn Haverbeke', '9781593279561', 5, 5);