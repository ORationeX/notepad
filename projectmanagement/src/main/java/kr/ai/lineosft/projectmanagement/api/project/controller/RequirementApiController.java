package kr.ai.lineosft.projectmanagement.api.project.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementHistoryResponse;
import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.RequirementService;
import kr.ai.lineosft.projectmanagement.global.security.CustomUserDetails;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class RequirementApiController {

    private final RequirementService requirementService;

    @GetMapping("/api/projects/{projectId}/requirements")
    public ResponseEntity<List<RequirementResponse>> getRequirements(@PathVariable Long projectId) {
        return ResponseEntity.ok(requirementService.getRequirements(projectId));
    }

    @GetMapping("/api/requirements/{id}")
    public ResponseEntity<RequirementResponse> getRequirement(@PathVariable Long id) {
        return ResponseEntity.ok(requirementService.getRequirement(id));
    }

    @GetMapping("/api/requirements/{id}/histories")
    public ResponseEntity<List<RequirementHistoryResponse>> getHistories(@PathVariable Long id) {
        return ResponseEntity.ok(requirementService.getHistories(id));
    }

    @PostMapping("/api/projects/{projectId}/requirements")
    public ResponseEntity<RequirementResponse> createRequirement(
            @PathVariable Long projectId,
            @Valid @RequestBody RequirementRequest request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        RequirementResponse created = requirementService.createRequirement(projectId, request, userDetails.getMember());
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/api/requirements/{id}")
    public ResponseEntity<RequirementResponse> updateRequirement(
            @PathVariable Long id,
            @Valid @RequestBody RequirementRequest request,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        return ResponseEntity.ok(requirementService.updateRequirement(id, request, userDetails.getMember()));
    }

    @DeleteMapping("/api/requirements/{id}")
    public ResponseEntity<Void> deleteRequirement(@PathVariable Long id) {
        requirementService.deleteRequirement(id);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/api/requirements/{id}/sync-progress")
    public ResponseEntity<RequirementResponse> syncProgressFromTasks(
            @PathVariable Long id,
            @AuthenticationPrincipal CustomUserDetails userDetails) {
        return ResponseEntity.ok(requirementService.syncProgressFromTasks(id, userDetails.getMember()));
    }
}
