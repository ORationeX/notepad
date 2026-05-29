package kr.ai.lineosft.projectmanagement.api.project.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.project.dto.SprintRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.SprintResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.SprintService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class SprintApiController {

    private final SprintService sprintService;

    @GetMapping("/api/projects/{projectId}/sprints")
    public ResponseEntity<List<SprintResponse>> getSprints(@PathVariable Long projectId) {
        return ResponseEntity.ok(sprintService.getSprints(projectId));
    }

    @PostMapping("/api/projects/{projectId}/sprints")
    public ResponseEntity<SprintResponse> createSprint(
            @PathVariable Long projectId,
            @Valid @RequestBody SprintRequest request) {
        SprintResponse createdSprint = sprintService.createSprint(projectId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdSprint);
    }

    @PutMapping("/api/sprints/{sprintId}")
    public ResponseEntity<SprintResponse> updateSprint(
            @PathVariable Long sprintId,
            @Valid @RequestBody SprintRequest request) {
        return ResponseEntity.ok(sprintService.updateSprint(sprintId, request));
    }

    @DeleteMapping("/api/sprints/{sprintId}")
    public ResponseEntity<Void> deleteSprint(@PathVariable Long sprintId) {
        sprintService.deleteSprint(sprintId);
        return ResponseEntity.noContent().build();
    }
}
