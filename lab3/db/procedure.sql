delimiter //
drop procedure if exists publication_insert //
create procedure publication_insert(in t_id char(5),in p_id int,in t_rank int,in t_corr bool,out debug int)
begin
	-- 主键要唯一
	-- 排名要唯一
    -- 通讯作者要唯一
	declare state int default 0;
    declare a int; -- 检查论文是否存在
    declare b int; -- 检查教师-论文记录是否存在
    declare c int; -- 检查论文当前rank是否有人
    declare d int; -- 检查论文通讯作者是否已存在
    declare continue handler for 1146 set state=1;
    declare continue handler for sqlstate '42S02' set state=2;
    declare continue handler for not found set state=3;
    declare continue handler for sqlexception set state=4;
    start transaction;
    select count(*) from paper where id=p_id into a;
    if a=1 then
    -- 论文已存在 
		select count(*) from publication where teacher_id=t_id and paper_id=p_id into b;
        if b=0 then
        -- 教师-论文记录还不存在
			select count(*) from publication where paper_id=p_id and ranking=t_rank into c;
            if c=0 then
			-- 当前论文当前rank还没有人
				if t_corr=true then 
                -- 当前教师是通讯作者
					select count(*) from publication where paper_id=p_id and correspond=true into d;
					if d=0 then
					-- 论文通讯作者还不存在
						insert into publication (teacher_id, paper_id, ranking, correspond) VALUES (t_id, p_id, t_rank, t_corr);
					else
                    -- 论文通讯作者已存在
						set state=-1;
					end if;
				else
				-- 当前教师不是通讯作者
					insert into publication (teacher_id, paper_id, ranking, correspond) VALUES (t_id, p_id, t_rank, t_corr);
				end if;
			else 
            -- 当前论文当前rank有人了
				set state=-2;
			end if;
		else
        -- 教师-论文记录已经存在（主键冲突）
			set state=-3;
		end if;
	else
	-- 论文不存在
		set state=-4;
	end if;

    if state=0 then
		set debug=0;
        commit;
	else
		set debug=state;
		rollback;
	end if;
end //
delimiter ;



delimiter //
drop procedure if exists proj_undertake_insert //
create procedure proj_undertake_insert(in t_id char(5),in p_id varchar(256),in t_rank int,in t_expense float,out debug int)
begin
	-- 主键要唯一
	-- 排名要唯一
    -- 经费和不能超总经费
	declare state int default 0;
    declare a int; -- 检查项目是否存在
    declare b int; -- 检查教师-项目记录是否存在
    declare c int; -- 检查项目当前rank是否有人
    declare d float; -- 检查项目当前经费和是否已超总经费
    declare tot_expense float;
    declare now_tot float;
    declare continue handler for 1146 set state=1;
    declare continue handler for sqlstate '42S02' set state=2;
    declare continue handler for not found set state=3;
    declare continue handler for sqlexception set state=4;
    start transaction;
    select count(*) from project where id=p_id into a;
    if a=1 then
    -- 项目已存在 
		select expenditure from project where id=p_id into tot_expense;
		select count(*) from proj_undertake where teacher_id=t_id and proj_id=p_id into b;
        if b=0 then
        -- 教师-项目记录还不存在
			select count(*) from proj_undertake where proj_id=p_id and ranking=t_rank into c;
            if c=0 then
			-- 当前项目当前rank还没有人
				select sum(expense) from proj_undertake where proj_id=p_id into now_tot;
                if now_tot is null then
					set now_tot=0;
				end if;
				if t_expense+now_tot<=tot_expense then 
                -- 当前项目当前经费和没有超总经费
					insert into proj_undertake (teacher_id, proj_id, ranking, expense) VALUES (t_id, p_id, t_rank, t_expense);
				else
				-- 当前项目当前经费和超总经费了
					set state=-1;
				end if;
			else 
            -- 当前项目当前rank有人了
				set state=-2;
			end if;
		else
        -- 教师-项目记录已经存在（主键冲突）
			set state=-3;
		end if;
	else
	-- 项目不存在
		set state=-4;
	end if;

    if state=0 then
		set debug=0;
        commit;
	else
		set debug=state;
		rollback;
	end if;
end //
delimiter ;

delimiter //
drop procedure if exists course_teach_insert //
create procedure course_teach_insert(in t_id char(5),in c_id varchar(256),in c_year int,in c_semester int,in t_hours int,out debug int)
begin
	-- 主键要唯一
    -- 学时和不能超总学时
	declare state int default 0;
    declare a int; -- 检查课程是否存在
    declare b int; -- 检查教师-课程记录是否存在
    declare c int; -- 检查课程当前学时和是否已超总学时
    declare tot_hours int;
    declare now_tot int;
    declare continue handler for 1146 set state=1;
    declare continue handler for sqlstate '42S02' set state=2;
    declare continue handler for not found set state=3;
    declare continue handler for sqlexception set state=4;
    start transaction;
    select count(*) from course where id=c_id into a;
    if a=1 then
    -- 课程已存在 
		select hours from course where id=c_id into tot_hours;
		select count(*) from course_teach where teacher_id=t_id and course_id=c_id into b;
        if b=0 then
        -- 教师-课程记录还不存在
			select sum(teach_hours) from course_teach where course_id=c_id into now_tot;
            if now_tot is null then
				set now_tot=0;
			end if;
			if t_hours+now_tot<=tot_hours then 
			-- 当前课程当前学时和没有超总学时
				insert into course_teach (teacher_id, course_id, year, semester, teach_hours) VALUES (t_id, c_id, c_year, c_semester, t_hours);
			else
			-- 当前课程当前学时和超总学时了
				set state=-1;
			end if;
		else
        -- 教师-课程记录已经存在（主键冲突）
			set state=-2;
		end if;
	else
	-- 课程不存在
		set state=-3;
	end if;

    if state=0 then
		set debug=0;
        commit;
	else
		set debug=state;
		rollback;
	end if;
end //
delimiter ;