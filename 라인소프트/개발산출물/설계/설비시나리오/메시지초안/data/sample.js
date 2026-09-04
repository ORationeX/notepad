window.MSG_SAMPLE_DOC = {
  "title": "설비 메시지 정의서",
  "versionLabel": "CISCO V4",
  "products": [
    {
      "id": "prd_001",
      "name": "Tele",
      "processes": [
        {
          "id": "prc_002",
          "name": "Active Align",
          "equipmentName": "-",
          "vendorName": "ISMEDIA",
          "sheetPrefix": "",
          "events": [
            {
              "id": "evt_003",
              "typeId": "BatchTrackIn",
              "note": "설비 미통신",
              "values": {},
              "rows": {}
            },
            {
              "id": "evt_004",
              "typeId": "BatchTrackOut",
              "note": "설비 미통신",
              "values": {},
              "rows": {}
            }
          ]
        },
        {
          "id": "prc_021",
          "name": "Laser Marking",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "Tele_LaserMarking",
          "events": [
            {
              "id": "evt_022",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_023",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        },
        {
          "id": "prc_027",
          "name": "PCB Recon",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "Tele_PCBRecon",
          "events": [
            {
              "id": "evt_028",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_029",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "id": "prd_005",
      "name": "Wide",
      "processes": [
        {
          "id": "prc_006",
          "name": "Active Align",
          "equipmentName": "-",
          "vendorName": "Envysolution",
          "sheetPrefix": "Wide_ActiveAlign",
          "events": [
            {
              "id": "evt_007",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {},
              "rows": {}
            },
            {
              "id": "evt_008",
              "typeId": "DB_to_DB",
              "note": "이동",
              "values": {},
              "rows": {
                "db_to_db": [
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_CT_L",
                    "value": 46.9284,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 중앙부(Center) Left 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_CT_T",
                    "value": 47.4911,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 중앙부(Center) Top 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_CT_R",
                    "value": 46.2899,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 중앙부(Center) Right 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_CT_B",
                    "value": 47.7132,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) Bottom 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_CT_Avg",
                    "value": 47.1056,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 중앙부(Center) 해상력 평균치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LT_L",
                    "value": 34.7018,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) Left 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LT_T",
                    "value": 45.2872,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) Top 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LT_R",
                    "value": 38.4084,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) Right 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LT_B",
                    "value": 41.1015,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) Bottom 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LT_Avg",
                    "value": 39.8747,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌상단(Left Top) 해상력 평균치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RT_L",
                    "value": 38.6858,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우상단(Right Top) Left 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RT_T",
                    "value": 39.9936,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우상단(Right Top) Top 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RT_R",
                    "value": 43.4124,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우상단(Right Top) Right 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RT_B",
                    "value": 49.582,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우상단(Right Top) Bottom 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RT_Avg",
                    "value": 42.9184,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우상단(Right Top) 해상력 평균치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LB_L",
                    "value": 33.8024,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌하단(Left Bottom) Left 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LB_T",
                    "value": 37.135,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌하단(Left Bottom) Top 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LB_R",
                    "value": 34.1064,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌하단(Left Bottom) Right 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LB_B",
                    "value": 35.224,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌하단(Left Bottom) Bottom 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_LB_Avg",
                    "value": 35.0669,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 좌하단(Left Bottom) 해상력 평균치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RB_L",
                    "value": 42.3168,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우하단(Right Bottom) Left 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RB_T",
                    "value": 36.7029,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우하단(Right Bottom) Top 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RB_R",
                    "value": 41.7024,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우하단(Right Bottom) Right 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RB_B",
                    "value": 41.863,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우하단(Right Bottom) Bottom 채널 해상력 수치"
                  },
                  {
                    "item": "SFR_AA_119lp/mm",
                    "site": "SFR_RB_Avg",
                    "value": 40.6463,
                    "desc": "Wide AA 공정(119lp/mm) 기준, 화면 우하단(Right Bottom) 해상력 평균치"
                  }
                ]
              }
            },
            {
              "id": "evt_009",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {},
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        },
        {
          "id": "prc_024",
          "name": "Laser Marking",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "Wide_LaserMarking",
          "events": [
            {
              "id": "evt_025",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_026",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        },
        {
          "id": "prc_030",
          "name": "PCB Recon",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "Wide_PCBRecon",
          "events": [
            {
              "id": "evt_031",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_032",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "id": "prd_010",
      "name": "VCM(Tele)",
      "processes": [
        {
          "id": "prc_011",
          "name": "Lens Assy",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "VCM_LensAssy",
          "events": [
            {
              "id": "evt_012",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_013",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "id": "prd_014",
      "name": "IR Base(Tele)",
      "processes": [
        {
          "id": "prc_015",
          "name": "IR_Filter Attach",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "IRBase_IFA",
          "events": [
            {
              "id": "evt_016",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_017",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        },
        {
          "id": "prc_018",
          "name": "Tape 제거",
          "equipmentName": "-",
          "vendorName": "OMT",
          "sheetPrefix": "IRBase_Tape제거",
          "events": [
            {
              "id": "evt_019",
              "typeId": "STDTrackIn",
              "note": "이동",
              "values": {
                "in_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "in_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {}
            },
            {
              "id": "evt_020",
              "typeId": "STDTrackOut",
              "note": "이동",
              "values": {
                "out_request": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                },
                "out_response": {
                  "lotID": {
                    "description": "Wet Boat QR"
                  }
                }
              },
              "rows": {
                "out_item_desc": [
                  {
                    "item": "resultStatus",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태를 표시 (OK,NG…)"
                  },
                  {
                    "item": "resultMessage",
                    "site": "",
                    "desc": "설비에서 작업한 결과 상태에 대한 메시지"
                  },
                  {
                    "item": "lensID",
                    "site": "",
                    "desc": "렌즈 개별 바코드"
                  },
                  {
                    "item": "sensorID",
                    "site": "",
                    "desc": "Sensor ID"
                  },
                  {
                    "item": "boatID",
                    "site": "",
                    "desc": "AA 보트 ID"
                  },
                  {
                    "item": "zone",
                    "site": "",
                    "desc": "작업구역(단일 작업구역일 경우 A)"
                  },
                  {
                    "item": "defectQuantity",
                    "site": "",
                    "desc": "불량 발생 총 Unit 수량"
                  },
                  {
                    "item": "defectCode",
                    "site": "",
                    "desc": "불량 발생시 코드 ID"
                  },
                  {
                    "item": "defectName",
                    "site": "",
                    "desc": "불량코드 ID의 명칭"
                  }
                ]
              }
            }
          ]
        }
      ]
    }
  ]
};
