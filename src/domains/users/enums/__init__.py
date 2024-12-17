from enum import Enum


class RoleEnum(Enum):
    ADMIN_SCMA = 60
    DEPT_HEAD = 10
    DIV_HEAD = 2
    DIRECTOR = 28
    PRESIDENT_DIRECTOR = 19


RoleDict = {
    RoleEnum.ADMIN_SCMA.value: "Admin SCMA",
    RoleEnum.DEPT_HEAD.value: "Department Head",
    RoleEnum.DIV_HEAD.value: "Division Head",
    RoleEnum.DIRECTOR.value: "Director",
    RoleEnum.PRESIDENT_DIRECTOR.value: "President Director",
}
