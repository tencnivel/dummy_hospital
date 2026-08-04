from fastapi import APIRouter

from dummy_hospital.api.v1 import doctors, exams, patients, units

router = APIRouter()
router.include_router(patients.router)
router.include_router(doctors.router)
router.include_router(units.router)
router.include_router(exams.router)
