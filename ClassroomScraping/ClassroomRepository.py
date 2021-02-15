import datetime


class ClassroomRepository:
    @staticmethod
    def get_courses(service, state="ACTIVE"):
        results = service.courses().list(courseStates=state).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')

        return courses

    @staticmethod
    def get_course(service, id_course, state="ACTIVE"):
        results = service.courses().get(id=id_course).execute()

        return results

    @staticmethod
    def announcements_course(service, id_course, max_announcements=0):
        result = service.courses().announcements().list(
            courseId=id_course, pageSize=max_announcements).execute()
        announcements = result.get('announcements', [])

        return announcements

    @staticmethod
    def new_announcements_account (service, now_time):
        courses = ClassroomRepository.get_courses(service)

        announcements_account = []
        for course in courses:
            course_announcements = ClassroomRepository.announcements_course(
                service, course['id'], 5)

            if (len(course_announcements) != 0):
                for announcement in course_announcements:
                    date_time_str = announcement['updateTime']
                    announcement_date_time = datetime.datetime.strptime(
                        date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

                    one_time = datetime.timedelta(minutes=30)
                    if (announcement_date_time < now_time - one_time):
                        break

                    announcements_account.append(announcement)

        return announcements_account

    @staticmethod
    def works_course(service, id_course, max_courses=0):
        result = service.courses().courseWork().list(
            courseId=id_course, pageSize=max_courses).execute()
        
        work = result.get('courseWork', [])

        return work
        
    @staticmethod
    def new_works_curse(service, id_course, now_time, max_couse=0):
        course_works = ClassroomRepository.works_course(
                service, id_course, 3)

        new_works_curse = []
        if (len(course_works) != 0):
            for work in course_works:
                date_time_str = work['updateTime']
                work_date_time = datetime.datetime.strptime(
                date_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

                one_time = datetime.timedelta(minutes=30)
                if (work_date_time < now_time - one_time):
                    break
                
                new_works_curse.append(work)

        return new_works_curse

    @staticmethod
    def new_works_account (service, now_time):
        courses = ClassroomRepository.get_courses(service)

        announcements_account = []
        for course in courses:
            new_works = ClassroomRepository.new_works_curse(service, course['id'], now_time, 3)
            announcements_account.extend(new_works)

        return announcements_account