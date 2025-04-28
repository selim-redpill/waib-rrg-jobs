# models.py
"""
Pydantic models for representing the Renault Retail Group car stock API response.

Defines schemas for individual car stock items, aggregation buckets, and overall response.
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel


class KeyCount(BaseModel):
    """
    Represents a single term aggregation bucket.

    Attributes:
        key: The bucket key (could be string or integer).
        count: Number of items in this bucket.
        value: Optional hex color code for buckets like colors.
    """
    key: Union[str, int]
    count: int
    value: Optional[str] = None


class StatValues(BaseModel):
    """
    Represents min/max values for a statistical aggregation.

    Attributes:
        min: Minimum observed value.
        max: Maximum observed value.
    """
    min: Union[int, float]
    max: Union[int, float]


class StatAgg(BaseModel):
    """
    Holds multiple statistical aggregations for numeric fields.

    Attributes:
        price: Aggregation for vehicle prices.
        mileage: Aggregation for odometer readings.
        hp: Aggregation for engine horsepower.
        monthlyPayment: Aggregation for financing payments.
        year: Aggregation for model years.
        emissionsCO2: Aggregation for CO2 emissions.
    """
    price: StatValues
    mileage: StatValues
    hp: StatValues
    monthlyPayment: StatValues
    year: StatValues
    emissionsCO2: StatValues


class Aggregations(BaseModel):
    """
    Top-level container for all aggregation data returned by the API.

    Attributes:
        term: Dictionary of term aggregations keyed by field name.
        stat: Statistical aggregations for numeric metrics.
    """
    term: Dict[str, List[KeyCount]]
    stat: StatAgg


class CarStockItem(BaseModel):
    """
    Schema for a single vehicle stock entry.

    Only key fields are included; lengthy arrays (images, diacOffers, etc.) are omitted.
    """
    id: int
    name: str
    brand: str
    model: str
    categoryName: Optional[str]
    colorName: Optional[str]
    weight: Optional[int]
    height: Optional[int]
    width: Optional[int]
    numberOfDoors: Optional[int]
    vehicleIdentificationNumber: str
    dateVehicleFirstRegistered: str
    fuelType: Optional[str]
    mileageFromOdometer: Optional[int]
    vehicleSeatingCapacity: Optional[int]
    vehicleTransmission: Optional[str]
    emissionsCO2: Optional[int]
    numberPlate: Optional[str]
    vehiclePriceIncTax: Optional[float]
    vehiclePriceExcTax: Optional[float]
    vehicleFamily: Optional[str]
    finishQuality: Optional[str]
    version: Optional[str]
    vehicleEnginePowerTax: Optional[int]
    vehicleEnginePowerHp: Optional[int]
    warrantyName: Optional[str]
    rrgType: Optional[str]
    locationName: Optional[str]
    dateOfEntryIntoStock: Optional[str]
    internalType: Optional[str]
    type: Optional[str]
    onlinePurchaseCompliant: Optional[bool]
    availabilityStatus: Optional[str]
    vcdAvailable: Optional[bool]
    location: Optional[str]


class CarStockResponse(BaseModel):
    """
    Schema for the overall API response.

    Attributes:
        totalItems: Total number of vehicles available.
        items: List of parsed CarStockItem objects.
        aggregations: Aggregation data for UI filters and stats.
    """
    totalItems: int
    items: List[CarStockItem]
    aggregations: Aggregations