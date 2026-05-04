class Course:
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain
        self.value = None
        
    def assign(self, value):
        self.value = value
    
    def remove_assignment(self):
        self.value = None
        
    def initialize(self, variables, domain):
        self.courses = []
        for variable in variables:
            course = Course(variable, domain.copy())
            self.courses.append(course)
        return self.courses
    def __str__(self):
        return f"{self.name}: {self.value}"


def initialize(variables, domain):
    courses = []
    for variable in variables:
        course = Course(variable, domain.copy())
        courses.append(course)
    return courses


def is_consistent(course, assignedCourses, constraints):
    assignedByName = {c.name: c for c in assignedCourses}
    for constraint in constraints:
        left, right = constraint.split("!=")
        if course.name != left and course.name != right:
            continue
        othername = right if course.name == left else left
        othercourse = assignedByName.get(othername)
        if othercourse is None or othercourse.value is None:
            continue
        if course.value == othercourse.value:
            return False
    return True


def backtracking(course, remainingCourses, assignedCourses, constraints):
    for day in course.domain:
        course.assign(day)
        if not is_consistent(course, assignedCourses, constraints):
            course.remove_assignment()
            continue
        assignedCourses.append(course)
        if not remainingCourses:
            return True
        nextCourse = remainingCourses[0]
        nextRemainingCourses = remainingCourses[1:]
        if backtracking(nextCourse, nextRemainingCourses, assignedCourses, constraints):
            return True
        assignedCourses.pop()
        course.remove_assignment()
    return False
from collections import deque
import copy


class Course:
    def __init__(self, name, domain) -> None:
        self.name = name
        self.domain = domain
        self.value = None

    def assign(self, value):
        self.value = value

    def remove_assignment(self):
        self.value = None

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"


def initialize(variables, domain) -> list[Course]:
    courses = []

    for variable in variables:
        course = Course(name=variable, domain=domain.copy())
        courses.append(course)

    return courses


def is_consistent(course: Course, assigned_courses: list[Course], constraints) -> bool:
    assigned_by_name = {
        assigned_course.name: assigned_course for assigned_course in assigned_courses
    }

    for constraint in constraints:
        left, right = constraint.split("!=")

        if course.name != left and course.name != right:
            continue

        other_name = right if course.name == left else left
        other_course = assigned_by_name.get(other_name)

        if other_course is None or other_course.value is None:
            continue

        if course.value == other_course.value:
            return False

    return True


def backtracking(
    course: Course,
    remaining_courses: list[Course],
    assigned_courses: list[Course],
    constraints: list[str],
) -> bool:
    for day in course.domain:
        course.assign(day)

        if not is_consistent(course, assigned_courses, constraints):
            course.remove_assignment()

            continue

        assigned_courses.append(course)

        if not remaining_courses:
            return True

        next_course = remaining_courses[0]
        next_remaining_courses = remaining_courses[1:]

        if backtracking(
            next_course, next_remaining_courses, assigned_courses, constraints
        ):
            return True

        assigned_courses.pop()
        course.remove_assignment()

    return False


def _neighbors(name: str, constraints: list[str]):
    result = []
    for constraint in constraints:
        left, right = constraint.split("!=")
        if name == left:
            result.append(right)
        elif name == right:
            result.append(left)
    return result    


def _arc_satisfied(x: str, y: str, X: Course, Y: Course, constraints: list[str]):
    for constraint in constraints:
        left, right = constraint.split("!=")

        if (X.name == left and Y.name == right) or (X.name == right and Y.name == left):

            if x == y:
                return False

    return True


def revise(X: Course, Y: Course, constraints: list[str]):
    revised = False

    for x in X.domain[:]:
        if not any(_arc_satisfied(x, y, X, Y, constraints) for y in Y.domain):
            X.domain.remove(x)
            revised = True

    return revised


def ac3(courses: list[Course], constraints: list[str]):
    course_map = {course.name: course for course in courses}
    queue = deque()
    for constraint in constraints:
        left, right = constraint.split("!=")
        queue.append((left, right))
        queue.append((right, left))
        
    while queue:
        x_name, y_name = queue.popleft()
        X = course_map[x_name]
        Y = course_map[y_name]

        if revise(X, Y, constraints):
            if not X.domain:
                return False
            for z_name in _neighbors(x_name, constraints):
                if z_name != y_name:
                    queue.append((z_name, x_name))
    return True
    


def select_mrv(unassigned: list[Course], constraints: list[str]):   
    min_size = len(unassigned[0].domain)
    actual_course = unassigned[0]
    for course in unassigned:
        if course.domain:
            if len(course.domain) < min_size:
                min_size = len(course.domain)
                actual_course = course
    return actual_course


def _degree(course: Course, unassigned_names, constraints: list[str]):
    count = 0
    for constraint in constraints:
        left, right = constraint.split("!=")
        if course.name == left and right in unassigned_names:
            count += 1
        elif course.name == right and left in unassigned_names:
            count += 1
    
    return count

   

def select_degree(unassigned: list[Course], constraints: list[str]):
    unassigned_names = {course.name for course in unassigned}

    for course in unassigned:
        course.degree = _degree(course, unassigned_names, constraints)

    actual_course = unassigned[0]
    for course in unassigned:
        if course.degree > actual_course.degree:
            actual_course = course
    return actual_course


def select_mrv_degree(unassigned: list[Course], constraints: list[str]):
    mrv_course = select_mrv(unassigned, constraints)
    min_size = len(mrv_course.domain)

    candidates = []
    for course in unassigned:
        if len(course.domain) == min_size:
            candidates.append(course)

    if len(candidates) == 1:
        return candidates[0]
    return select_degree(candidates, constraints)


def _select_first(unassigned: list[Course], constraints: list[str]):
    return unassigned[0]


def backtracking_with_inference(
    unassigned: list[Course],
    assigned: list[Course],
    constraints: list[str],
    select=_select_first,
):
    
    if not unassigned:
        return True
    course = select(unassigned, constraints)
    remaining = [c for c in unassigned if c != course]
    
    for day in course.domain:
        course.assign(day)

        if not is_consistent(course, assigned, constraints):
            course.remove_assignment()
            continue
        assigned.append(course)
        all_courses = assigned + remaining
        saved_domains = {c.name: c.domain[:] for c in all_courses}
        course.domain = [day]
        inference_ok = ac3(all_courses, constraints)
        if inference_ok:
            if backtracking_with_inference(remaining, assigned, constraints, select):
                return True
        for c in all_courses:
            c.domain = saved_domains[c.name]
        assigned.remove(course)
        course.remove_assignment()
    return False

   
