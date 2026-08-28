import sys
import os
import unittest
import math
import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.entities.player import Player
from src.entities.player_weapons import WeaponController
from src.entities.weapons import (
    BaseWeaponBehavior, WeaponFireContext, get_weapon_behavior,
    PulseBehavior, RapidBehavior, ScatterBehavior, MissileBehavior,
    BarrageBehavior, PlasmaBehavior, RailgunBehavior,
    ContinuousBeamBehavior, TeslaBehavior, ClusterBehavior, EMPBehavior
)
from src.data.game_data import (
    WEAPON_PULSE, WEAPON_RAPID, WEAPON_SCATTER, WEAPON_MISSILE,
    WEAPON_BARRAGE, WEAPON_PLASMA, WEAPON_RAIL, WEAPON_BEAM,
    WEAPON_TESLA, WEAPON_CLUSTER, WEAPON_EMP, WEAPON_DEFS
)
from src.entities.bullet import (
    Bullet, HomingMissile, BarrageMissile, HeavyPlasmaOrb,
    RailgunSlug, ContinuousBeam, TeslaArcBeam, ClusterTorpedo, EMPPulse
)


class TestWeaponArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        if not pygame.display.get_surface():
            pygame.display.set_mode((100, 100), pygame.NOFRAME)

    def test_behavior_registry_resolution(self):
        """Verify all 11 active weapon IDs resolve to their dedicated modular behaviors."""
        expected = {
            WEAPON_PULSE: PulseBehavior,
            WEAPON_RAPID: RapidBehavior,
            WEAPON_SCATTER: ScatterBehavior,
            WEAPON_MISSILE: MissileBehavior,
            WEAPON_BARRAGE: BarrageBehavior,
            WEAPON_PLASMA: PlasmaBehavior,
            WEAPON_RAIL: RailgunBehavior,
            WEAPON_BEAM: ContinuousBeamBehavior,
            WEAPON_TESLA: TeslaBehavior,
            WEAPON_CLUSTER: ClusterBehavior,
            WEAPON_EMP: EMPBehavior,
        }
        for w_id, cls_type in expected.items():
            behavior = get_weapon_behavior(w_id)
            self.assertIsInstance(behavior, cls_type, f"Weapon {w_id} failed to resolve to {cls_type}")

    def test_unknown_weapon_fails_explicitly(self):
        """Verify an invalid weapon ID raises KeyError explicitly and does not silently fall back to Pulse."""
        with self.assertRaises(KeyError):
            get_weapon_behavior("invalid_unknown_superweapon")

        with self.assertRaises(KeyError):
            get_weapon_behavior("")

    def test_pulse_behavior_overdrive_fan(self):
        """Verify Pulse fires 1 bullet normally and 3 bullets under Overdrive mode."""
        player = Player((500, 400))
        player.set_weapon(WEAPON_PULSE)

        # Normal fire
        bullets_normal = player.shoot((800, 400))
        self.assertEqual(len(bullets_normal), 1)
        self.assertIsInstance(bullets_normal[0], Bullet)

        # Overdrive fire
        player.weapon_cooldowns[WEAPON_PULSE] = 0.0
        player.trigger_overdrive()
        bullets_od = player.shoot((800, 400))
        self.assertEqual(len(bullets_od), 3)

    def test_rapid_behavior_alternating_mounts(self):
        """Verify Rapid alternating mount points between dual_left and dual_right."""
        player = Player((500, 400))
        player.set_drone_class("interceptor")
        player.set_weapon(WEAPON_RAPID)

        player.weapon_cooldowns[WEAPON_RAPID] = 0.0
        b1 = player.shoot((800, 400))
        self.assertEqual(len(b1), 1)

        player.weapon_cooldowns[WEAPON_RAPID] = 0.0
        b2 = player.shoot((800, 400))
        self.assertEqual(len(b2), 1)

        # Origin positions should differ in Y (left vs right)
        self.assertNotEqual(b1[0].pos.y, b2[0].pos.y)

    def test_scatter_behavior_five_projectiles(self):
        """Verify Scatter fires 5 spread projectiles."""
        player = Player((500, 400))
        player.set_weapon(WEAPON_SCATTER)
        player.weapon_cooldowns[WEAPON_SCATTER] = 0.0

        bullets = player.shoot((800, 400))
        self.assertEqual(len(bullets), 5)
        for b in bullets:
            self.assertIsInstance(b, Bullet)

    def test_homing_missile_behavior(self):
        """Verify Missile weapon spawns HomingMissile."""
        player = Player((500, 400))
        player.set_weapon(WEAPON_MISSILE)
        player.weapon_cooldowns[WEAPON_MISSILE] = 0.0

        bullets = player.shoot((800, 400))
        self.assertEqual(len(bullets), 1)
        self.assertIsInstance(bullets[0], HomingMissile)

    def test_barrage_behavior_four_missiles(self):
        """Verify Barrage weapon spawns 4 BarrageMissile instances."""
        player = Player((500, 400))
        player.set_drone_class("command")
        player.set_weapon(WEAPON_BARRAGE)
        player.weapon_cooldowns[WEAPON_BARRAGE] = 0.0

        bullets = player.shoot((800, 400))
        self.assertEqual(len(bullets), 4)
        for b in bullets:
            self.assertIsInstance(b, BarrageMissile)

    def test_plasma_and_railgun_behaviors(self):
        """Verify Plasma and Railgun spawn their specialized projectile classes."""
        player = Player((500, 400))

        # Plasma
        player.set_weapon(WEAPON_PLASMA)
        player.weapon_cooldowns[WEAPON_PLASMA] = 0.0
        plasma_bullets = player.shoot((800, 400))
        self.assertEqual(len(plasma_bullets), 1)
        self.assertIsInstance(plasma_bullets[0], HeavyPlasmaOrb)

        # Railgun
        player.set_weapon(WEAPON_RAIL)
        player.weapon_cooldowns[WEAPON_RAIL] = 0.0
        rail_bullets = player.shoot((800, 400))
        self.assertEqual(len(rail_bullets), 1)
        self.assertIsInstance(rail_bullets[0], RailgunSlug)

    def test_beam_behavior_lifecycle(self):
        """Verify ContinuousBeam instantiates, tracks, and cleans up when fire stops."""
        player = Player((500, 400))
        player.set_drone_class("arc")
        player.set_weapon(WEAPON_BEAM)
        player.weapon_cooldowns[WEAPON_BEAM] = 0.0

        # Frame 1: Fired
        beams = player.shoot((800, 400))
        self.assertEqual(len(beams), 1)
        self.assertIsInstance(beams[0], ContinuousBeam)
        self.assertIsNotNone(player.weapons.active_beam)

        # Frame 1 update: retains active beam
        player.update(0.016)
        self.assertIsNotNone(player.weapons.active_beam)

        # Frame 2 update without shooting: beam terminates
        player.update(0.016)
        self.assertIsNone(player.weapons.active_beam)

    def test_tesla_cluster_emp_behaviors(self):
        """Verify Tesla, Cluster, and EMP spawn their specialized projectile types."""
        player = Player((500, 400))

        # Tesla
        player.set_weapon(WEAPON_TESLA)
        player.weapon_cooldowns[WEAPON_TESLA] = 0.0
        b_tesla = player.shoot((800, 400))
        self.assertIsInstance(b_tesla[0], TeslaArcBeam)

        # Cluster
        player.set_weapon(WEAPON_CLUSTER)
        player.weapon_cooldowns[WEAPON_CLUSTER] = 0.0
        b_cluster = player.shoot((800, 400))
        self.assertIsInstance(b_cluster[0], ClusterTorpedo)

        # EMP
        player.set_weapon(WEAPON_EMP)
        player.weapon_cooldowns[WEAPON_EMP] = 0.0
        b_emp = player.shoot((800, 400))
        self.assertIsInstance(b_emp[0], EMPPulse)


if __name__ == "__main__":
    unittest.main()
