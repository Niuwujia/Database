select id,name as cname,hours,property,tname,year,semester,teach_hours from course left outer join (
	select id as tid,name as tname,year,semester,teach_hours from course_teach, teacher where id=teacher_id
)temp on id=tid;


-- paperid-作者
select paper_id, group_concat(new_name order by ranking) as authors from (
select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id
) temp group by paper_id;



-- paperid-通讯作者
select paper_id, group_concat(name) as corr_author from publication left outer join teacher on teacher_id=id and correspond=1 group by paper_id;

-- 呈现论文一览表
select id, name, publish_source, publish_year, type, level, authors, corr_author
from paper, (select paper_id, group_concat(new_name order by ranking) as authors from (
select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id
) temp group by paper_id) temp1,
(select paper_id, group_concat(name) as corr_author from publication left outer join teacher on teacher_id=id and correspond=1 group by paper_id) temp2
where id=temp1.paper_id and id=temp2.paper_id;

-- 呈现项目申报一览表
select id, name, source, type, expenditure, now_expend, start_year, finish_year, applicants
from project, (select proj_id, group_concat(new_name order by ranking) as applicants from (
select proj_id, concat(name, '(', ranking, ')') as new_name, ranking from proj_undertake, teacher where teacher_id=id
) temp group by proj_id) temp1,
(select proj_id, round(sum(IFNULL(expense, 0)), 2) as now_expend from proj_undertake group by proj_id) temp2
where id=temp1.proj_id and id=temp2.proj_id;

-- 呈现授课一览表
select id, name, hours, now_hours, property, year, semester, lecturers, concat(id, ',', year, ',', semester) as PK
from course, (select course_id, group_concat(new_name) as lecturers, year, semester from (
select course_id, concat(name, '(', teach_hours, ')') as new_name, year, semester from course_teach, teacher where teacher_id=id
) temp group by course_id, year, semester) temp1,
(select course_id, year as year2, semester as semester2, sum(IFNULL(teach_hours, 0)) as now_hours from course_teach group by course_id, year, semester) temp2
where id=temp1.course_id and id=temp2.course_id and temp1.year=temp2.year2 and temp1.semester=temp2.semester2;









