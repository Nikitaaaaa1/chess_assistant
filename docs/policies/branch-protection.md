# Polityka Ochrony Gałęzi (Branch Protection Policy)

Aby uniemożliwić bezpośredni wypchnięcie zmian (push) do kluczowych gałęzi z poziomu konsoli, należy skonfigurować zasady ochrony w interfejsie GitHub.

## Kluczowe Zasady:
1.  **Główne gałęzie podlegające ochronie**: `main`, `develop`.
2.  **Wymagany Pull Request**: Każda zmiana musi przejść przez PR przed włączeniem do gałęzi.
3.  **Wymagane Sprawdzenia (Checks)**: PR musi przejść pomyślnie wszystkie testy CI (`Vision Service CI`, `Logic API CI`, `Web UI CI`) przed zatwierdzeniem.
4.  **Brak bezpośredniego wypychania**: Blokada `git push origin main` oraz `git push origin develop`.

## Instrukcja konfiguracji na GitHub:

1.  Przejdź do repozytorium na GitHub.
2.  Kliknij **Settings** -> **Branches**.
3.  W sekcji **Branch protection rules** kliknij **Add rule**.
4.  Dla gałęzi `main`:
    *   **Branch name pattern**: `main`
    *   Zaznacz: **Require a pull request before merging**.
    *   Zaznacz: **Require status checks to pass before merging**.
    *   Wyszukaj i dodaj zadania CI: `test-and-lint`, `build-and-test`.
    *   Zaznacz: **Restrict pushes** (jeśli dostępne) lub polegaj na wymogu PR.
5.  Powtórz kroki dla gałęzi `develop`.

## Mandat Agenta (GEMINI.md):
Agent ma kategoryczny zakaz wykonywania `git push` bezpośrednio do gałęzi `main` oraz `develop`. Każda propozycja zmian musi zostać zaprezentowana w oddzielnej gałęzi funkcyjnej (`feat/`, `fix/` itp.), a następnie zgłoszona jako Pull Request po uzyskaniu zgody użytkownika.
