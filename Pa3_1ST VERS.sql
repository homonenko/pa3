create database pa3_pets;

use pa3_pets;

create table owners
(
    id varchar(36) primary key,
    first_name varchar(100) not null,
    last_name varchar(100) not null,
    phone varchar(15) not null,
    email varchar(200)
);

alter table owners
comment = 'table to store pet owner information';

alter table owners
modify column id varchar(36) comment 'unique identifier for each owner',
modify column first_name varchar(100) not null comment 'first name of the owner',
modify column last_name varchar(100) not null comment 'last name of the owner',
modify column phone varchar(15) not null comment 'number of the owner',
modify column email varchar(200) comment 'email of the owner';


create table pets
(
    id varchar(36) primary key,
    owner_id varchar(36) not null,
    pet_name varchar(100) not null,
    species varchar(50),
    breed varchar(50),
    age int,
    foreign key (owner_id) references owners(id)
);

alter table pets
comment = 'table to store pet information';

create table veterinarians
(
    id varchar(36) primary key,
    first_name varchar(100),
    last_name varchar(100),
    phone varchar(15),
    email varchar(200),
    specialty varchar(100)
);

alter table veterinarians
comment = 'table to store veterinarian info';


create table services
(
    id varchar(36) primary key,
    service_name varchar(100),
    description varchar(500),
    price decimal(10, 2)
);

alter table services
comment = 'table to store the pet care services';

create table pet_medical_records
(
    id varchar(36) primary key,
    pet_id varchar(36) unique, 
    vaccination_status varchar(100),
    foreign key (pet_id) references pets(id)
);
alter table pet_medical_records
comment = 'table to store the pet medical record and the pet, so that 1:1 relationship table is made';

create table appointments
(
    id varchar(36) primary key,
    pet_id varchar(36) not null,
    veterinarian_id varchar(36),
    appointment_date date,
    status varchar(20),
    foreign key (pet_id) references pets(id),
    foreign key (veterinarian_id) references veterinarians(id)
);

alter table appointments
comment = 'table to store pet appointments for services';

alter table appointments
modify column id varchar(36) comment 'unique id for each appointment',
modify column pet_id varchar(36) comment 'id for the pet getting the service',
modify column veterinarian_id varchar(36) comment 'id for the vet giving the service',
modify column appointment_date date comment 'date of the appointment',
modify column status varchar(20) comment 'status of the appointment (scheduled, completed)';

create table appointment_services (
    appointment_id varchar(36),
    service_id varchar(36),
    primary key (appointment_id, service_id),
    foreign key (appointment_id) references appointments(id),
    foreign key (service_id) references services(id)
);

alter table appointment_services
comment = 'many:many relationship between appointments and services';

alter table owners modify phone varchar(50);
alter table veterinarians modify phone varchar(50);

create index index_owner_id on pets(owner_id);
create index index_pet_id on appointments(pet_id);
create index index_veterinarian_id on appointments(veterinarian_id);
create index index_service_id on appointments(service_id);
create index index_appointment_date on appointments(appointment_date);

SELECT o.first_name, o.last_name, p.pet_name
FROM owners o
JOIN pets p ON o.id = p.owner_id
WHERE p.species = 'Dog';

create user 'pet_user'@'localhost' identified by '123321123';
grant select on pa3_pets.* to 'pet_user'@'localhost';
show grants for 'pet_user'@'localhost';


create user 'pet_data_entry'@'localhost' identified by 'pass123';
grant insert on pa3_pets.* to 'pet_data_entry'@'localhost';
show grants for 'pet_data_entry'@'localhost';


create user 'pet_admin'@'localhost' identified by 'admin321123';
grant select, insert, update, delete on pa3_pets.* to 'pet_admin'@'localhost';
show grants for 'pet_admin'@'localhost';


create or replace view appointment_details as
select 
    a.id as appointment_id,
    p.pet_name as pet_name,
    v.first_name as veterinarian_first_name,
    v.last_name as veterinarian_last_name,
    v.specialty as veterinarian_specialty,
    a.appointment_date as appointment_date,
    a.status as appointment_status
from appointments a
join pets p on a.pet_id = p.id
left join veterinarians v on a.veterinarian_id = v.id
join appointment_services aps on a.id = aps.appointment_id
join services s on aps.service_id = s.id
group by a.id, p.pet_name, v.first_name, v.last_name, v.specialty, a.appointment_date, a.status;

create procedure add_service()
insert into services (service_name, description, price)
values ('some service', 'cool service', 500.00);

сreate trigger set_default_status
before insert on appointments
for each row
begin
    if new.status is null then
        set new.status = 'scheduled';
    end if;
end;

