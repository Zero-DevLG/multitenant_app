from app.business.verification.application.evaluate_status import CompositeStatusEvaluator

class BuildOperatorOverviewService:
    def __init__(self, rules_repo, answers_repo):
        self._rules_repo = rules_repo
        self._answers_repo = answers_repo
        self._evaluator = CompositeStatusEvaluator(rules_repo, answers_repo)
        
    async def build(self, operator_id: int, module_id: int | None = None, section_id: int | None = None) -> dict:
        print(f"datos: {module_id}, {section_id}")
        all_answers = await self._answers_repo.get_all_answers_for_operator(operator_id)
        answer_by_field_id = {a.section_field_rule_id: a for a in all_answers}
        
        reference_ids = [a.reference_id for a in all_answers if a.reference_id]
        references_by_id = await self._answers_repo.get_reference_answers_by_ids(reference_ids)
        
        print(f"references {references_by_id}")
        
        file_ids = [r.file_id for r in references_by_id.values() if r.file_id]
        address_ids = [r.address_id for r in references_by_id.values() if r.address_id]
        files_by_id = await self._answers_repo.get_files_by_ids(file_ids)
        addresses_by_id = await self._answers_repo.get_addresses_by_ids(address_ids)
        
        modules_payload = []
        modules = []
        sections = []
        
        if module_id:
            m = await self._rules_repo.get_module_by_id(module_id)
            modules.append(m)
        else:
            modules = await self._rules_repo.get_all_modules()
            
        print(f"Modulos requeridos:{modules}")
        for module in modules :
            section_payload = []
            if section_id:
                sections.append(await self._rules_repo.get_section_by_id(section_id))
            else:
                sections = await self._rules_repo.get_sections_by_module(module.id)
            for section in sections:
                field_rules = await self._rules_repo.get_field_rules(section.id)
                fields_payload = [
                    await self._build_field(rule,  answer_by_field_id.get(rule.id), references_by_id ,files_by_id, addresses_by_id)
                    for rule in field_rules
                ]
                
                section_status = await self._evaluator.evaluate_section(operator_id, section.id)
                section_payload.append({
                    "name": section.name, "code":section.code, "required": section.required,
                    "status": section_status, "fields": fields_payload
                })
                
            module_status = await self._evaluator.evaluate_module(operator_id, module.id)
            modules_payload.append({
                "name": module.name,  "code": module.code, "required": module.required,
                "status": module_status, "sections": section_payload,
            })
        return {"modules": modules_payload}
    
    async def _build_field(self, rule, answer, references_by_id, files_by_id, addresses_by_id) -> dict:
        base = {
            "code": rule.code, "type": rule.type, "required": rule.required,
            "validation_state": answer.validation_state if answer else "missing",
            "observations": answer.observations if answer else None,
            "value": None
        }
        
        if rule.type == "file":
            data = await self._rules_repo.get_field_file_types(rule.id)
            base["type_file_id"] = data.get('id')
            base["type_file_key"] = data.get('key')
            base["name_file"] = data.get("name")
        
        if answer is None or answer.reference_id is None:
            if answer and rule.type == "text":
                base["value"] == answer.value_text
            return base
        
        ref = references_by_id.get(answer.reference_id)
        if ref is None:
            return base
        
        if rule.type == "text":
            base["value"] = answer.value_text
        elif rule.type == "file" and ref.file_id:
            doc = files_by_id.get(ref.file_id)
            if doc:
                base["value"] = {"field_id": doc.id, "name": doc.name, "type_file_id": doc.type_file_id, "url": doc.url}
        elif rule.type == "address" and ref.address_id:
            addr = addresses_by_id.get(ref.address_id)
            if addr:
                base["value"] = {
                    "address_id": addr.id, "street": addr.street, "city": addr.city,
                    "state": addr.state, "zip_code": addr.zip_code, "country": addr.country,
                    "address_type_id": addr.address_type_id,
                }
        return base