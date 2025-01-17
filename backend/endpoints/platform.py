from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import Optional

from handler import dbh
from utils.oauth import protected_route
from config import ROMM_HOST

router = APIRouter()

WEBRCADE_SUPPORTED_PLATFORM_SLUGS = [
    "3do",
    "arcade",
    "atari2600",
    "atari5200",
    "atari7800",
    "lynx",
    "wonderswan",
    "wonderswan-color",
    "colecovision",
    "turbografx16--1",
    "turbografx-16-slash-pc-engine-cd",
    "supergrafx",
    "pc-fx",
    "nes",
    "n64",
    "snes",
    "gb",
    "gba",
    "gbc",
    "virtualboy",
    "sg1000",
    "sms",
    "genesis-slash-megadrive",
    "segacd",
    "gamegear",
    "neo-geo-cd",
    "neogeoaes",
    "neogeomvs",
    "neo-geo-pocket",
    "neo-geo-pocket-color",
    "ps",
]

WEBRCADE_SLUG_TO_TYPE_MAP = {
    "atari2600": "2600",
    "atari5200": "5200",
    "atari7800": "7800",
    "lynx": "lnx",
    "turbografx16--1": "pce",
    "turbografx-16-slash-pc-engine-cd": "pce",
    "supergrafx": "sgx",
    "pc-fx": "pcfx",
    "virtualboy": "vb",
    "genesis-slash-megadrive": "genesis",
    "gamegear": "gg",
    "neogeoaes": "neogeo",
    "neogeomvs": "neogeo",
    "neo-geo-cd": "neogeocd",
    "neo-geo-pocket": "ngp",
    "neo-geo-pocket-color": "ngc",
    "ps": "psx",
}


class PlatformSchema(BaseModel):
    slug: str
    fs_slug: str
    igdb_id: Optional[int] = None
    sgdb_id: Optional[int] = None
    name: Optional[str]
    logo_path: str
    rom_count: int

    class Config:
        from_attributes = True


@protected_route(router.get, "/platforms", ["platforms.read"])
def platforms(request: Request) -> list[PlatformSchema]:
    """Returns platforms data"""
    return dbh.get_platforms()


@protected_route(router.get, "/platforms/webrcade/feed", [])
def platforms_webrcade_feed(request: Request):
    """Returns platforms data"""
    platforms = dbh.get_platforms()

    with dbh.session.begin() as session:
        return {
            "title": "RomM Feed",
            "longTitle": "Custom RomM Feed",
            "description": "Custom feed from your RomM library",
            "thumbnail": "https://raw.githubusercontent.com/zurdi15/romm/f2dd425d87ad8e21bf47f8258ae5dcf90f56fbc2/frontend/assets/isotipo.svg",
            "background": "https://raw.githubusercontent.com/zurdi15/romm/release/.github/screenshots/gallery.png",
            "categories": [
                {
                    "title": p.name,
                    "longTitle": f"{p.name} Games",
                    "background": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-background.png",
                    "thumbnail": f"{ROMM_HOST}/assets/webrcade/feed/{p.slug.lower()}-thumb.png",
                    "description": "",
                    "items": [
                        {
                            "title": rom.name,
                            "description": rom.summary,
                            "type": WEBRCADE_SLUG_TO_TYPE_MAP.get(p.slug, p.slug),
                            "thumbnail": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_s}",
                            "background": f"{ROMM_HOST}/assets/romm/resources/{rom.path_cover_l}",
                            "props": {"rom": f"{ROMM_HOST}{rom.download_path}"},
                        }
                        for rom in session.scalars(dbh.get_roms(p.slug)).all()
                    ],
                }
                for p in platforms
                if p.slug in WEBRCADE_SUPPORTED_PLATFORM_SLUGS
            ],
        }
