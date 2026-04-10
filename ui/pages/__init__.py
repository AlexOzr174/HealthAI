# Страницы интерфейса HealthAI
from .onboarding import OnboardingPage
from .dashboard import DashboardPage
from .diary import DiaryPage
from .planner import PlannerPage
from .recipes import RecipesPage
from .achievements import AchievementsPage
from .settings_notifications import SettingsNotificationsPage
from .settings_diets import SpecialDietsPage
from .settings_api import APIIntegrationPage

__all__ = [
    'OnboardingPage', 'DashboardPage', 'DiaryPage',
    'PlannerPage', 'RecipesPage', 'AchievementsPage',
    'SettingsNotificationsPage', 'SpecialDietsPage', 'APIIntegrationPage'
]
