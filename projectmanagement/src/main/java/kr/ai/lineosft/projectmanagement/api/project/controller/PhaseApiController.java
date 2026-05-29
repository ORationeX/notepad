package kr.ai.lineosft.projectmanagement.api.project.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.project.dto.PhaseRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.PhaseResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.PhaseService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class PhaseApiController {

    private final PhaseService phaseService;

    @GetMapping("/api/projects/{projectId}/phases")
    public ResponseEntity<List<PhaseResponse>> getPhases(@PathVariable Long projectId) {
        return ResponseEntity.ok(phaseService.getPhases(projectId));
    }

    @PostMapping("/api/projects/{projectId}/phases")
    public ResponseEntity<PhaseResponse> createPhase(
            @PathVariable Long projectId,
            @Valid @RequestBody PhaseRequest request) {
        PhaseResponse createdPhase = phaseService.createPhase(projectId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdPhase);
    }

    @PutMapping("/api/phases/{phaseId}")
    public ResponseEntity<PhaseResponse> updatePhase(
            @PathVariable Long phaseId,
            @Valid @RequestBody PhaseRequest request) {
        return ResponseEntity.ok(phaseService.updatePhase(phaseId, request));
    }

    @DeleteMapping("/api/phases/{phaseId}")
    public ResponseEntity<Void> deletePhase(@PathVariable Long phaseId) {
        phaseService.deletePhase(phaseId);
        return ResponseEntity.noContent().build();
    }
}
