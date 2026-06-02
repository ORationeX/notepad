package kr.ai.lineosft.projectmanagement.api.project.controller;

import jakarta.validation.Valid;
import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectDiagramRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.ProjectDiagramResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.ProjectDiagramService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
public class ProjectDiagramApiController {

    private final ProjectDiagramService projectDiagramService;

    @GetMapping("/requirements/{requirementId}/diagrams")
    public ResponseEntity<List<ProjectDiagramResponse>> getDiagramsByRequirement(@PathVariable Long requirementId) {
        return ResponseEntity.ok(projectDiagramService.getDiagramsByRequirement(requirementId));
    }

    @GetMapping("/diagrams/{id}")
    public ResponseEntity<ProjectDiagramResponse> getDiagram(@PathVariable Long id) {
        return ResponseEntity.ok(projectDiagramService.getDiagram(id));
    }

    @PostMapping("/requirements/{requirementId}/diagrams")
    public ResponseEntity<ProjectDiagramResponse> createDiagram(
            @PathVariable Long requirementId,
            @Valid @RequestBody ProjectDiagramRequest request) {
        ProjectDiagramResponse created = projectDiagramService.createDiagram(requirementId, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/diagrams/{id}")
    public ResponseEntity<ProjectDiagramResponse> updateDiagram(
            @PathVariable Long id,
            @Valid @RequestBody ProjectDiagramRequest request) {
        return ResponseEntity.ok(projectDiagramService.updateDiagram(id, request));
    }

    @DeleteMapping("/diagrams/{id}")
    public ResponseEntity<Void> deleteDiagram(@PathVariable Long id) {
        projectDiagramService.deleteDiagram(id);
        return ResponseEntity.noContent().build();
    }
}
