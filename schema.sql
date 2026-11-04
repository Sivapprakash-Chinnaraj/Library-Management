DROP TABLE IF EXISTS borrowings;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- Unified Users Table for Role-Based Access Control
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, -- In production, we will hash this
    role ENUM('staff', 'student') NOT NULL,
    phone VARCHAR(50),
    registered_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    added_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE borrowings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'Issued',
    FOREIGN KEY (book_id) REFERENCES books (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert starter accounts to test the login system
-- Password for all is 'password123'
INSERT INTO users (name, email, password, role, phone) VALUES 
('Library Admin', 'admin@library.com', 'password123', 'staff', '555-0000'),
('Alice Smith', 'alice@example.com', 'password123', 'student', '555-0101'),
('Bob Jones', 'bob@example.com', 'password123', 'student', '555-0202');

-- Insert 85 starter books (50 Tech, 25 Fiction, 10 Manga)
INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES 
-- Tech Books
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
('Eloquent JavaScript', 'Marijn Haverbeke', '9781593279561', 5, 5),
-- Fiction Books
('1984', 'George Orwell', '9780451524935', 6, 6),
('To Kill a Mockingbird', 'Harper Lee', '9780060935467', 5, 5),
('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 4, 4),
('Pride and Prejudice', 'Jane Austen', '9780141439518', 3, 3),
('The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 5, 5),
('The Lord of the Rings', 'J.R.R. Tolkien', '9780544003415', 3, 3),
('The Hobbit', 'J.R.R. Tolkien', '9780547928227', 4, 4),
('Fahrenheit 451', 'Ray Bradbury', '9781451673319', 6, 6),
('Jane Eyre', 'Charlotte Brontë', '9780141441146', 2, 2),
('Animal Farm', 'George Orwell', '9780451526342', 5, 5),
('Brave New World', 'Aldous Huxley', '9780060850524', 4, 4),
('The Grapes of Wrath', 'John Steinbeck', '9780143039433', 2, 2),
('Moby-Dick', 'Herman Melville', '9780142437247', 3, 3),
('Frankenstein', 'Mary Shelley', '9780141439471', 4, 4),
('Dracula', 'Bram Stoker', '9780141439846', 3, 3),
('The Odyssey', 'Homer', '9780140268867', 2, 2),
('The Iliad', 'Homer', '9780140275360', 2, 2),
('Crime and Punishment', 'Fyodor Dostoevsky', '9780140449136', 3, 3),
('The Brothers Karamazov', 'Fyodor Dostoevsky', '9780374528379', 2, 2),
('War and Peace', 'Leo Tolstoy', '9781400079988', 1, 1),
('Anna Karenina', 'Leo Tolstoy', '9780143035008', 3, 3),
('The Alchemist', 'Paulo Coelho', '9780062315007', 7, 7),
('The Little Prince', 'Antoine de Saint-Exupéry', '9780156012195', 5, 5),
('The Chronicles of Narnia', 'C.S. Lewis', '9780066238500', 4, 4),
('Dune', 'Frank Herbert', '9780441172719', 6, 6),
-- Manga
('One Piece, Vol. 1', 'Eiichiro Oda', '9781569319017', 5, 5),
('Naruto, Vol. 1', 'Masashi Kishimoto', '9781569319000', 4, 4),
('Bleach, Vol. 1', 'Tite Kubo', '9781591164418', 3, 3),
('Attack on Titan, Vol. 1', 'Hajime Isayama', '9781612620244', 6, 6),
('Fullmetal Alchemist, Vol. 1', 'Hiromu Arakawa', '9781591169208', 4, 4),
('Death Note, Vol. 1', 'Tsugumi Ohba', '9781421501680', 5, 5),
('Dragon Ball, Vol. 1', 'Akira Toriyama', '9781569319208', 3, 3),
('My Hero Academia, Vol. 1', 'Kohei Horikoshi', '9781421582696', 6, 6),
('Demon Slayer, Vol. 1', 'Koyoharu Gotouge', '9781974700523', 7, 7),
('Jujutsu Kaisen, Vol. 1', 'Gege Akutami', '9781974710027', 5, 5);
