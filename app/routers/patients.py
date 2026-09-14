import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


# ---------------------------------------------------------
# GET /patients
# ---------------------------------------------------------

@router.get(
    "",
    response_model=schemas.APIResponse[List[schemas.PatientResponse]],
)
def list_patients(
    last_name: Optional[str] = Query(default=None),
    date_of_birth: Optional[date] = Query(default=None),
    phone_number: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        patients = crud.get_patients(
            db=db,
            last_name=last_name,
            date_of_birth=date_of_birth,
            phone_number=phone_number,
        )

        data = [
            schemas.PatientResponse.model_validate(patient)
            for patient in patients
        ]

        return {
            "data": data,
            "error": None,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while retrieving patients"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve patients",
        )


# ---------------------------------------------------------
# GET /patients/{patient_id}
# ---------------------------------------------------------

@router.get(
    "/{patient_id}",
    response_model=schemas.APIResponse[schemas.PatientResponse],
)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):
    patient = crud.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    return {
        "data": schemas.PatientResponse.model_validate(patient),
        "error": None,
    }


# ---------------------------------------------------------
# GET /patients/by-phone/{phone_number}
# VAPI LOOKUP ENDPOINT
# ---------------------------------------------------------

@router.get(
    "/by-phone/{phone_number}",
    response_model=Optional[schemas.PatientResponse],
)
def get_patient_by_phone_route(
    phone_number: str,
    db: Session = Depends(get_db),
):
    try:
        patient = crud.get_patient_by_phone(
            db,
            phone_number,
        )

        if not patient:
            return None

        return schemas.PatientResponse.model_validate(
            patient
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except SQLAlchemyError:
        logger.exception(
            "Database error while looking up patient by phone"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve patient",
        )


# ---------------------------------------------------------
# POST /patients
# VAPI CREATE PATIENT ENDPOINT
# ---------------------------------------------------------

@router.post(
    "",
    status_code=201,
    response_model=schemas.PatientResponse,
)
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
):
    try:

        existing = crud.get_patient_by_phone(
            db,
            patient.phone_number,
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="A patient with this phone number already exists",
            )

        created = crud.create_patient(
            db,
            patient,
        )

        logger.info(
            "Patient created: %s",
            patient.model_dump(mode="json"),
        )

        return schemas.PatientResponse.model_validate(
            created
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()

        logger.exception(
            "Database error while creating patient"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to save patient",
        )


# ---------------------------------------------------------
# PUT /patients/{patient_id}
# ---------------------------------------------------------

@router.put(
    "/{patient_id}",
    response_model=schemas.APIResponse[schemas.PatientResponse],
)
def update_patient(
    patient_id: str,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db),
):
    patient = crud.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    if patient_update.phone_number:

        duplicate = crud.get_patient_by_phone(
            db,
            patient_update.phone_number,
        )

        if (
            duplicate
            and duplicate.patient_id != patient_id
        ):
            raise HTTPException(
                status_code=400,
                detail="A patient with this phone number already exists",
            )

    try:

        updated = crud.update_patient(
            db,
            patient,
            patient_update,
        )

        logger.info(
            "Patient updated: patient_id=%s data=%s",
            patient_id,
            patient_update.model_dump(
                exclude_unset=True,
                mode="json",
            ),
        )

        return {
            "data": schemas.PatientResponse.model_validate(updated),
            "error": None,
        }

    except SQLAlchemyError:

        db.rollback()

        logger.exception(
            "Database error while updating patient %s",
            patient_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to update patient",
        )


# ---------------------------------------------------------
# DELETE /patients/{patient_id}
# ---------------------------------------------------------

@router.delete(
    "/{patient_id}",
    response_model=schemas.APIResponse[schemas.DeleteResponse],
)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
):

    patient = crud.get_patient(
        db,
        patient_id,
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found",
        )

    try:

        deleted = crud.soft_delete_patient(
            db,
            patient,
        )

        logger.info(
            "Patient soft-deleted: %s",
            patient_id,
        )

        return {
            "data": {
                "patient_id": deleted.patient_id,
                "deleted": True,
            },
            "error": None,
        }

    except SQLAlchemyError:

        db.rollback()

        logger.exception(
            "Database error while deleting patient %s",
            patient_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to delete patient",
        )