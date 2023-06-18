create table teacher(
	id char(5) primary key,
	name varchar(256),
	sex int check(sex in (1, 2)),
	title int check(title >= 1 and title <= 11)
);

create table paper(
	id int primary key,
    name varchar(256),
    publish_source varchar(256),
    publish_year date,
    type int check(type in (1, 2, 3, 4)),
	level int check(level >= 1 and level <= 6)
);

create table project(
	id varchar(256) primary key,
    name varchar(256),
    source varchar(256),
    type int check(type >= 1 and type <= 5),
    expenditure float,
    start_year int,
    finish_year int,
    check(finish_year >= start_year)
);

create table course(
	id varchar(256) primary key,
    name varchar(256),
    hours int,
    property int check(property in (1, 2))
);

create table publication(
	teacher_id char(5),
    paper_id int,
    ranking int,
    correspond bool,
    primary key(
		teacher_id,
		paper_id
	),
	foreign key(teacher_id) references teacher(id),
	foreign key(paper_id) references paper(id)
);

create table proj_undertake(
	teacher_id char(5),
    proj_id varchar(256),
    ranking int,
    expense float,
    primary key(
		teacher_id,
		proj_id
	),
	foreign key(teacher_id) references teacher(id),
	foreign key(proj_id) references project(id)
);

create table course_teach(
	teacher_id char(5),
    course_id varchar(256),
    year int,
    semester int check(semester in (1, 2, 3)),
    teach_hours int,
    primary key(
		teacher_id,
		course_id,
        year,
        semester
	),
	foreign key(teacher_id) references teacher(id),
	foreign key(course_id) references course(id)
);


-- drop table teacher; 
-- drop table course_teach;

-- 修改为级联删除模式
-- 先查看约束名称
show create table publication;
ALTER TABLE publication DROP FOREIGN KEY publication_ibfk_1;
ALTER TABLE publication DROP FOREIGN KEY publication_ibfk_2;
ALTER TABLE publication ADD CONSTRAINT FK_Teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE CASCADE;
ALTER TABLE publication ADD CONSTRAINT FK_Paper FOREIGN KEY (paper_id) REFERENCES paper(id) ON DELETE CASCADE;

show create table proj_undertake;
ALTER TABLE proj_undertake DROP FOREIGN KEY proj_undertake_ibfk_1;
ALTER TABLE proj_undertake DROP FOREIGN KEY proj_undertake_ibfk_2;
ALTER TABLE proj_undertake ADD CONSTRAINT FK_Teacher2 FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE CASCADE;
ALTER TABLE proj_undertake ADD CONSTRAINT FK_Proj FOREIGN KEY (proj_id) REFERENCES project(id) ON DELETE CASCADE;

show create table course_teach;
ALTER TABLE course_teach DROP FOREIGN KEY course_teach_ibfk_1;
ALTER TABLE course_teach DROP FOREIGN KEY course_teach_ibfk_2;
ALTER TABLE course_teach ADD CONSTRAINT FK_Teacher3 FOREIGN KEY (teacher_id) REFERENCES teacher(id) ON DELETE CASCADE;
ALTER TABLE course_teach ADD CONSTRAINT FK_Course FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE;

-- 创建视图
create view paper_view as
select id, name, publish_source, publish_year, type, level, authors, corr_author
from paper, (select paper_id, group_concat(new_name order by ranking) as authors from (
select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id
) temp group by paper_id) temp1,
(select paper_id, group_concat(name) as corr_author from publication left outer join teacher on teacher_id=id and correspond=1 group by paper_id) temp2
where id=temp1.paper_id and id=temp2.paper_id;
-- 视图无法同步更新，弃用
drop view paper_view;


set foreign_key_checks =0;

truncate table publication;

truncate table proj_undertake;

truncate table course_teach;

set foreign_key_checks =1;

select * from publication;

select * from proj_undertake;

select * from course_teach;