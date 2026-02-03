# Library Updates

This document tracks the library updates made to the Epilepsy12 application.

## Date: 2026-02-03

### Python Dependencies Updated ✓

The following Python packages in `requirements/requirements.txt` have been updated to their latest stable versions:

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| requests | 2.32.4 | 2.32.5 | Patch update |
| django | 5.2.9 | 5.2.11 | Patch update for security |
| pandas | 2.2.3 | 2.3.3 | Minor update, staying on 2.x for compatibility |
| azure-identity | 1.22.0 | 1.25.1 | Minor update |
| plotly | 6.0.1 | 6.5.2 | Minor update |
| gunicorn | 23.0.0 | 25.0.1 | Major version update |
| coverage | 7.8.0 | 7.8.2 | Patch update |
| rapidfuzz | 3.13.0 | 3.14.3 | Minor update |

### JavaScript Libraries Requiring Updates

The following JavaScript libraries need to be updated manually due to network restrictions in the build environment:

#### Currently Used Versions:
- **htmx**: 1.8.4 → **Latest: 2.0.7** (Major version update)
- **_hyperscript**: 0.9.12 → **Latest: 0.9.12** (Already current)
- **SweetAlert2**: 11.11.0 → **Latest: 11.26.18** (Minor update)
- **Plotly.js**: 1.58.5 → **Latest: 2.38.1** (Major version update)

#### CDN References to Replace:
1. **Popper.js** in `templates/rest_framework/api.html`:
   - Current: `https://cdn.jsdelivr.net/npm/popper.js@1.14.3/dist/umd/popper.min.js`
   - Action: Download v2.11.8 and host locally

2. **SweetAlert2** in `templates/epilepsy12/partials/registration/registration_dates.html`:
   - Current: `https://cdn.jsdelivr.net/npm/sweetalert2@11`
   - Action: Replace with local version reference

### How to Update JavaScript Libraries

A script `update_js_libraries.sh` has been created to automate the download process:

```bash
./update_js_libraries.sh
```

This script will:
1. Download the latest versions of all JavaScript libraries
2. Place them in appropriately versioned directories under `static/`
3. Provide instructions for updating template references

### Template Files Requiring Updates

After running the update script, the following template files need to be modified:

1. **templates/base.html**:
   ```html
   <!-- Update these lines: -->
   <script src="{% static 'plotly_1.58.5/plotly.min.js' %}"></script>
   <!-- TO: -->
   <script src="{% static 'plotly_2.38.1/plotly.min.js' %}"></script>

   <script src="{% static 'htmx_1.8.4/htmx.min.js' %}"></script>
   <!-- TO: -->
   <script src="{% static 'htmx_2.0.7/htmx.min.js' %}"></script>

   <script src="{% static 'sweetalert2_11.11.0/sweetalert2.all.min.js' %}"></script>
   <!-- TO: -->
   <script src="{% static 'sweetalert2_11.26.18/sweetalert2.all.min.js' %}"></script>
   ```

2. **templates/rest_framework/api.html**:
   ```html
   <!-- Replace CDN reference: -->
   <script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.3/dist/umd/popper.min.js" ...></script>
   <!-- WITH local reference: -->
   <script src="{% static 'popper_2.11.8/popper.min.js' %}"></script>
   ```

3. **templates/epilepsy12/partials/registration/registration_dates.html**:
   ```html
   <!-- Replace CDN reference: -->
   <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
   <!-- WITH local reference: -->
   <script src="{% static 'sweetalert2_11.26.18/sweetalert2.all.min.js' %}"></script>
   ```

### Breaking Changes & Compatibility Notes

#### htmx 2.0
- htmx 2.0 includes breaking changes from 1.x
- Major changes include:
  - Some attributes have been renamed
  - Event naming conventions have changed
  - Review the migration guide: https://htmx.org/migration-guide-htmx-1/
- **Action**: Test all HTMX functionality thoroughly after update

#### Plotly.js 2.x
- Plotly 2.x may have API changes from 1.x
- Review compatibility with Python plotly package (now at 6.5.2)
- **Action**: Test all charts and visualizations after update

#### Gunicorn 25.x
- Major version bump from 23.x
- Review release notes for any configuration changes needed
- **Action**: Test application startup and performance

### Testing Checklist

After applying updates, test the following:

- [ ] Application starts successfully
- [ ] Django admin panel works
- [ ] All HTMX interactions (form submissions, dynamic loading)
- [ ] SweetAlert2 popups and confirmations
- [ ] Plotly charts render correctly
- [ ] Two-factor authentication flow
- [ ] Date picker functionality (registration dates)
- [ ] API endpoints (REST framework)
- [ ] Run full test suite: `pytest`
- [ ] Run security scan: CodeQL

### Security Considerations

- All CDN references have been identified for replacement with local hosting
- This improves security posture by:
  - Eliminating external dependencies at runtime
  - Preventing potential CDN compromise
  - Improving application reliability
  - Meeting security audit requirements (Issue #571)

### Rollback Plan

If issues are encountered:
1. Revert changes to `requirements/requirements.txt`
2. Revert template updates
3. Remove new static library directories
4. Run `pip install -r requirements/requirements.txt`
5. Run `python manage.py collectstatic`

### Future Maintenance

- Consider setting up Dependabot or similar automated dependency checking
- Schedule regular library update reviews (quarterly recommended)
- Document any library-specific version constraints
- Keep this document updated with each library update cycle
