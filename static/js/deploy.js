angular.module("app.validation.rule", ["validation"]).config(["$validationProvider", function(t) {
    var e = {
            projectName: /^([\w-]+)$/,
            projectNameUnique: function(t) {
                var e = angular.injector(["ProjectServices"]),
                    a = e.get("Project");
                return a.checkName({
                    name: t
                }).$promise.then(function(t) {
                    return t.result
                })
            },
            verUnique: function(t, e) {
                var a = angular.injector(["ProjectServices"]),
                    o = a.get("Project");
                return o.checkVer({
                    ver: t,
                    projectId: e.$parent.projectId
                }).$promise.then(function(t) {
                    return t.result
                })
            },
            approvalSheetTemplateNameUnique: function(t, e) {
                var a = angular.injector(["ApprovalSheetTemplatesServices"]),
                    o = a.get("ApprovalSheetTemplate");
                return o.checkName({
                    name: t,
                    project_id: e.$parent.projectId
                }).$promise.then(function(t) {
                    return t.result
                })
            },
            semVer: /(\d+)\.(\d+)\.(\d+)/,
            noop: /.*/,
            repoUrl: /^git@(.+)hunantv\.com:(.+)$/
        },
        a = {
            required: {
                error: "必填项不能为空",
                success: "OK"
            },
            url: {
                error: "网址格式有误",
                success: "OK"
            },
            email: {
                error: "邮箱格式有误",
                success: "OK"
            },
            number: {
                error: "数字格式有误",
                success: "OK"
            },
            projectName: {
                error: "项目名格式有误",
                success: "OK"
            },
            projectNameUnique: {
                error: "此项目名称已存在",
                success: "OK"
            },
            verUnique: {
                error: "此版本号已存在",
                success: "OK"
            },
            semVer: {
                error: "版本格式有误",
                success: "OK"
            },
            approvalSheetTemplateNameUnique: {
                error: "此模板名称已存在",
                success: "OK"
            },
            repoUrl: {
                error: "仓库地址格式有误",
                success: "OK"
            }
        };
    t.setExpression(e).setDefaultMsg(a)
}]);
var app = angular.module("ainur", ["ui.router", "ui.bootstrap", "angular-loading-bar", "ngCookies", "ApiClient3Mod", "HostsServices", "ProjectServices", "ProjectVersionServices", "OperationRecordServices", "ApprovalSheetTemplatesServices", "ApprovalSheetsServices", "ProjectAppServices", "SysUsersServices", "AppInstanceServices", "AppVersionServices", "HostsControllers", "ProjectsControllers", "ProjectVersionsControllers", "UserSessionsControllers", "OperationRecordsControllers", "ApprovalSheetTemplatesControllers", "ApprovalSheetsControllers", "ProjectAppsControllers", "AppInstancesControllers", "AppVersionsControllers", "app.validation.rule"]);
app.config(["$stateProvider", "$urlRouterProvider", "$httpProvider", "$validationProvider", "$provide", function(t, e, a, o, s) {
    a.defaults.xsrfCookieName = "csrftoken", a.defaults.xsrfHeaderName = "X-CSRFToken", s.factory("httpExceptionIntercept", ["$q", "$injector", function(t, e) {
        return {
            responseError: function(a) {
                var o = e.get("$modal"),
                    s = e.get("$rootScope"),
                    l = s.$new();
                switch (a.status) {
                    case 403:
                        var r = e.get("$state");
                        r.go(a.data.message ? "aclTips" : "loginTips");
                        break;
                    case 500:
                        var i = e.get("$sce");
                        l.errorBody = i.trustAsHtml(a.data), o.open({
                            templateUrl: "modalHandler500.html",
                            scope: l,
                            size: "lg",
                            controller: "ModalCtrl"
                        });
                        break;
                    case 400:
                        l.errors = a.data, o.open({
                            templateUrl: "modalHandler400.html",
                            scope: l,
                            size: "lg",
                            controller: "ModalCtrl"
                        })
                }
                return t.reject(a)
            }
        }
    }]), a.interceptors.push("httpExceptionIntercept"), o.setErrorHTML(function(t) {
        return '<p class="help-block validation-invalid">' + t + "</p>"
    }), o.showSuccessMessage = !1;
    var l = o.validate;
    o.validate = function(t) {
        return jQuery("form[name=" + t.$name + "]").addClass("submit-clicked"), l.apply(this, arguments)
    }, e.otherwise("/home"), t.state("hosts", {
        url: "/hosts",
        templateUrl: "hosts/index.html",
        controller: "HostsCtrl"
    }).state("home", {
        url: "/home",
        templateUrl: "home.html"
    }).state("hosts.home", {
        url: "/home",
        templateUrl: "hosts/home.html"
    }).state("hosts.hostDetail", {
        url: "/hostDetail/{hostId}",
        templateUrl: "hosts/hostDetail.html",
        controller: "HostsHostDetailCtrl"
    }).state("softDetail", {
        url: "/softDetail",
        templateUrl: "hosts/softDetail.html",
        controller: "HostsSoftDetailCtrl"
    }).state("hosts.deploy", {
        url: "/deploy/{hostIds}",
        templateUrl: "hosts/deploy.html",
        controller: "HostsNewDeployCtrl"
    }).state("hosts.hostSaltJobList", {
        url: "/hostSaltJobList?hostId",
        templateUrl: "hosts/hostSaltJobList.html",
        controller: "HostSaltJobListCtrl"
    }).state("hosts.editFile", {
        url: "/editFile/{hostIds}",
        templateUrl: "hosts/editFile.html",
        controller: "HostsEditFileCtrl"
    }).state("hosts.modules", {
        url: "/modules/{nodeId}",
        templateUrl: "hosts/modules.html",
        controller: "HostsModulesCtrl"
    }).state("hosts.initEnv", {
        url: "/initEnv/{hostIds}",
        templateUrl: "hosts/initEnv.html",
        controller: "HostsInitEnvCtrl"
    }).state("sidebar", {
        url: "/sidebar",
        templateUrl: "projects/sidebar.html",
        controller: "SidebarCtrl"
    }).state("projectIndex", {
        url: "/projects",
        controller: "ProjectIndexCtrl",
        templateUrl: "projects/index.html"
    }).state("projectNew", {
        url: "/projects/new",
        controller: "ProjectNewCtrl",
        templateUrl: "projects/new.html"
    }).state("sidebar.projectShow", {
        url: "/projects/{projectId}",
        controller: "ProjectShowCtrl",
        templateUrl: "projects/show.html"
    }).state("sidebar.projectLog", {
        url: "/projects/{projectId}/log",
        controller: "ProjectLogCtrl",
        templateUrl: "projects/log.html"
    }).state("sidebar.projectEdit", {
        url: "/projects/{projectId}/edit",
        controller: "ProjectEditCtrl",
        templateUrl: "projects/edit.html"
    }).state("sidebar.projectVersionNew", {
        url: "/projectVersions/new?projectId",
        controller: "ProjectVersionNewCtrl",
        templateUrl: "projectVersions/new.html"
    }).state("sidebar.projectVersionIndex", {
        url: "/projectVersions?projectId",
        controller: "ProjectVersionIndexCtrl",
        templateUrl: "projectVersions/index.html"
    }).state("sidebar.projectVersionShow", {
        url: "/projectVersions/{projectVersionId}?projectId",
        controller: "ProjectVersionShowCtrl",
        templateUrl: "projectVersions/show.html"
    }).state("sidebar.approvalSheetTemplateNew", {
        url: "/approvalSheetTemplates/new?projectId",
        controller: "ApprovalSheetTemplateNewCtrl",
        templateUrl: "approvalSheetTemplates/new.html"
    }).state("sidebar.approvalSheetTemplateShow", {
        url: "/approvalSheetTemplates/{approvalSheetTemplateId}?projectId",
        controller: "ApprovalSheetTemplateShowCtrl",
        templateUrl: "approvalSheetTemplates/show.html"
    }).state("sidebar.approvalSheetTemplateIndex", {
        url: "/approvalSheetTemplates?projectId",
        controller: "ApprovalSheetTemplateIndexCtrl",
        templateUrl: "approvalSheetTemplates/index.html"
    }).state("sidebar.approvalSheetTemplateEdit", {
        url: "/approvalSheetTemplates/{approvalSheetTemplateId}/edit?projectId",
        controller: "ApprovalSheetTemplateEditCtrl",
        templateUrl: "approvalSheetTemplates/edit.html"
    }).state("sidebar.approvalSheetNew", {
        url: "/approvalSheets/new?projectId",
        controller: "ApprovalSheetNewCtrl",
        templateUrl: "approvalSheets/new.html"
    }).state("sidebar.approvalSheetShow", {
        url: "/approvalSheets/{approvalSheetId}?projectId",
        controller: "ApprovalSheetShowCtrl",
        templateUrl: "approvalSheets/show.html"
    }).state("sidebar.approvalSheetIndex", {
        url: "/approvalSheets?projectId",
        controller: "ApprovalSheetIndexCtrl",
        templateUrl: "approvalSheets/index.html"
    }).state("hosts.operationRecordIndex", {
        url: "/operationRecords",
        controller: "OperationRecordIndexCtrl",
        templateUrl: "operationRecords/index.html"
    }).state("projectAppIndex", {
        url: "/projectApps",
        controller: "ProjectAppIndexCtrl",
        templateUrl: "projectApps/index.html"
    }).state("projectAppNew", {
        url: "/projectApps/new",
        controller: "ProjectAppNewCtrl",
        templateUrl: "projectApps/new.html"
    }).state("appVersionIndex", {
        url: "/appVersions?appid",
        controller: "AppVersionIndexCtrl",
        templateUrl: "appVersions/index.html"
    }).state("appVersionNew", {
        url: "/appVersions/new?appid",
        controller: "AppVersionNewCtrl",
        templateUrl: "appVersions/new.html"
    }).state("appInstanceIndex", {
        url: "/appInstances?appid",
        controller: "AppInstanceIndexCtrl",
        templateUrl: "appInstances/index.html"
    }).state("appInstanceNew", {
        url: "/appInstances/new?appid",
        controller: "AppInstanceNewCtrl",
        templateUrl: "appInstances/new.html"
    }).state("appDomainNew", {
        url: "/appDomains/new?appid",
        controller: "AppDomainNewCtrl",
        templateUrl: "appDomains/new.html"
    }).state("appDomainIndex", {
        url: "/appDomains?appid",
        controller: "AppDomainIndexCtrl",
        templateUrl: "appDomains/index.html"
    }).state("appLogIndex", {
        url: "/appLogs",
        controller: "AppLogIndexCtrl",
        templateUrl: "appLogs/index.html"
    }).state("hosts.operationRecordReport", {
        url: "/operationRecordReport",
        controller: "OperationRecordReportCtrl",
        templateUrl: "operationRecords/report.html"
    }).state("loginTips", {
        url: "/loginTips",
        templateUrl: "loginTips.html"
    }).state("aclTips", {
        url: "/aclTips",
        templateUrl: "aclTips.html"
    }).state("help", {
        url: "/help",
        templateUrl: "help/index.html"
    }).state("help.home", {
        url: "/help/home",
        templateUrl: "help/home.html"
    }).state("help.hdeploy", {
        url: "/help/hdeploy",
        templateUrl: "help/hdeploy.html"
    }).state("help.conf", {
        url: "/help/conf",
        templateUrl: "help/conf.html"
    }).state("help.init", {
        url: "/help/init",
        templateUrl: "help/init.html"
    }).state("help.contact", {
        url: "/help/contact",
        templateUrl: "help/contact.html"
    })
}]).controller("ModalCtrl", ["$scope", "$modalInstance", function(t, e) {
    t.closeModal = function() {
        e.close()
    }
}]), angular.module("ApiClient3Mod", ["ngResource"]).factory("ApiClient3", ["$http", "$q", "$window", function(t, e, a) {
    var o = {},
        s = function(t) {
            var o = t.data;
            return 0 !== o.code ? (a.alert("接口" + t.config.url + "出错, 错误信息: " + t.data.message), e.reject(t)) : o
        };
    return o.get = function() {
        var e = arguments[0],
            a = arguments[1];
        return t.get(e, {
            params: a
        }).then(s)
    }, o.post = function() {
        var e = arguments[0],
            a = arguments[1];
        return t.post(e, jQuery.param(a), {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
            }
        }).then(s)
    }, o
}]), angular.module("HostsServices", ["ngResource"]).factory("Host", ["$resource", function(t) {
    return t("/deploy/api/hosts/:hostId", null, {
        deploy: {
            method: "POST",
            url: "/deploy/api/hosts/deploy"
        },
        readHostFile: {
            method: "GET",
            url: "/deploy/api/hosts/read_host_file"
        },
        deployHostFile: {
            method: "POST",
            url: "/deploy/api/hosts/deploy_host_file"
        },
        initEnv: {
            method: "POST",
            url: "/deploy/api/hosts/init_env"
        }
    })
}]).factory("Soft", ["$resource", function(t) {
    return t("/deploy/api/salt_states/:hostId")
}]).factory("HostSaltJob", ["$resource", function(t) {
    return t("/deploy/api/host_salt_jobs/:hostSaltJobId", null, {
        project_jobs: {
            method: "GET",
            url: "/deploy/api/host_salt_jobs/project_jobs",
            isArray: !0
        }
    })
}]).factory("HostSaltJobUtils", [function() {
    var t = {};
    return t.getBgClass = function(t) {
        return 2 === t.status || 3 === t.status ? "danger" : 1 === t.status ? "success" : ""
    }, t
}]).factory("SoftDetail", ["$resource", function(t) {
    return t("/deploy/api/soft_detail/")
}]), angular.module("ProjectServices", ["ngResource"]).factory("Project", ["$resource", function(t) {
    return t("/deploy/api/projects/:projectId", null, {
        gitRefs: {
            method: "GET",
            url: "/deploy/api/projects/:projectId/git_refs",
            isArray: !0
        },
        baseImages: {
            method: "GET",
            url: "/deploy/api/base_images",
            isArray: !0
        },
        getPods: {
            method: "GET",
            url: "/deploy/api/pods",
            isArray: !0
        },
        getGroups: {
            method: "GET",
            url: "/deploy/api/groups",
            isArray: !0
        },
        checkName: {
            method: "GET",
            url: "/deploy/api/projects/check_name",
            isArray: !1
        },
        checkVer: {
            method: "GET",
            url: "/deploy/api/projects/:projectId/check_ver",
            isArray: !1
        },
        update: {
            method: "PATCH",
            url: "/deploy/api/projects/:projectId",
            isArray: !1
        }
    })
}]).factory("ProjectUtils", [function() {
    var t = {};
    return t.shAceOption = {
        theme: "github",
        mode: "sh"
    }, t.handleSelectTree = function(t) {
        var e = t.hostCat;
        return function(t, a) {
            e.treeInstance = a.instance, e.selectedHosts = [], jQuery.each(a.selected, function() {
                var t = a.instance.get_node(this);
                if ("host" === t.data.node_type) {
                    var o = {
                        id: t.data.id,
                        ip: t.text
                    };
                    e.selectedHosts.push(o)
                }
            })
        }
    }, t.expandTree = function(t) {
        jQuery.each(t.instance._model.data, function(e) {
            /^project_(name|env).*/.test(e) && t.instance.open_node(e)
        })
    }, t.addHostToEnv = function(t, e) {
        jQuery.each(e.selectedHosts, function(a, o) {
            var s = !1;
            jQuery.each(e.hosts, function(e, a) {
                return a.id === o.id ? (a.isProd = t, s = !0, !1) : void 0
            }), s || e.hosts.push({
                id: o.id,
                ip: o.ip,
                isProd: t
            })
        }), e.selectedHosts = [], e.treeInstance && e.treeInstance.deselect_all()
    }, t.removeHost = function(t, e) {
        for (var a = -1, o = 0, s = e.hosts.length; s > o; o++) e.hosts[o].id === t && (a = o);
        e.hosts.splice(a, 1)
    }, t
}]), angular.module("ProjectVersionServices", ["ngResource"]).factory("ProjectVersion", ["$resource", function(t) {
    return t("/deploy/api/project_versions/:projectVersionId", null, {
        deploy: {
            method: "POST",
            url: "/deploy/api/project_versions/:projectVersionId/deploy",
            isArray: !1
        },
        rollback: {
            method: "POST",
            url: "/deploy/api/project_versions/:projectVersionId/rollback",
            isArray: !1
        },
        retryApiTest: {
            method: "POST",
            url: "/deploy/api/project_versions/:projectVersionId/retry_api_test",
            isArray: !1
        },
        drawing: {
            method: "GET",
            url: "/deploy/api/project_versions/:projectVersionId/drawing",
            isArray: !1
        }
    })
}]), angular.module("OperationRecordServices", ["ngResource"]).factory("OperationRecord", ["$resource", function(t) {
    return t("/deploy/api/operation_records/:operationRecordId", null, {
        queryAll: {
            method: "GET",
            url: "/deploy/api/operation_records/query_all",
            isArray: !1
        },
        queryProject: {
            method: "GET",
            url: "/deploy/api/operation_records/query_project",
            isArray: !0
        },
        queryUser: {
            method: "GET",
            url: "/deploy/api/operation_records/query_user",
            isArray: !0
        }
    })
}]), angular.module("ApprovalSheetTemplatesServices", ["ngResource"]).factory("ApprovalSheetTemplate", ["$resource", function(t) {
    return t("/deploy/api/approval_sheet_templates/:approvalSheetTemplateId", null, {
        update: {
            method: "PATCH",
            url: "/deploy/api/approval_sheet_templates/:approvalSheetTemplateId",
            isArray: !1
        },
        checkName: {
            method: "GET",
            url: "/deploy/api/approval_sheet_templates/check_name",
            isArray: !1
        }
    })
}]), angular.module("ApprovalSheetsServices", ["ngResource"]).factory("ApprovalSheet", ["$resource", function(t) {
    return t("/deploy/api/approval_sheets/:approvalSheetId", null, {
        audit: {
            method: "POST",
            url: "/deploy/api/approval_sheets/:approvalSheetId/audit",
            isArray: !1
        },
        deploy: {
            method: "POST",
            url: "/deploy/api/approval_sheets/:approvalSheetId/deploy",
            isArray: !1
        },
        rollback: {
            method: "POST",
            url: "/deploy/api/approval_sheets/:approvalSheetId/rollback",
            isArray: !1
        }
    })
}]), angular.module("ProjectAppServices", ["ngResource"]).factory("ProjectApp", ["ApiClient3", function(t) {
    var e = {};
    return e.options = function() {
        return t.get("/console/data/get")
    }, e.list = function(e) {
        return t.get("/console/app/list", e)
    }, e.create = function(e) {
        return t.post("/console/app/create", e)
    }, e.deploy = function(e) {
        return t.post("/console/app/deploy", e)
    }, e.destroy = function(e) {
        return t.post("/console/app/delete", e)
    }, e.update = function(e) {
        return t.post("/console/app/update", e)
    }, e.gitRefs = function(e) {
        return t.get("/console/gitinfo/get", {
            appid: e
        })
    }, e.logList = function(e) {
        return t.get("/console/log/list", e)
    }, e.createAppDomain = function(e) {
        return t.post("/console/domain/add", e)
    }, e.destroyAppDomain = function(e) {
        return t.post("/console/domain/delete", e)
    }, e.listAppDomain = function(e) {
        return t.get("/console/domain/list", e)
    }, e.updateRouter = function(e) {
        return t.post("/console/router/update", e)
    }, e
}]), angular.module("SysUsersServices", ["ngResource"]).factory("SysUser", ["$resource", function(t) {
    return t("/deploy/api/sys_users/:sysUserId")
}]), angular.module("AppVersionServices", ["ngResource"]).factory("AppVersion", ["ApiClient3", function(t) {
    var e = {};
    return e.list = function(e) {
        return t.get("/console/version/list", e)
    }, e.create = function(e) {
        return t.post("/console/version/create", e)
    }, e.setAsCurrent = function(e) {
        return t.post("/console/currentversion/set", e)
    }, e.manualBuild = function(e) {
        return t.post("/console/version/build", e)
    }, e
}]), angular.module("AppInstanceServices", ["ngResource"]).factory("AppInstance", ["ApiClient3", function(t) {
    var e = {};
    return e.list = function(e) {
        return t.get("/console/ins/list", e)
    }, e.create = function(e) {
        return t.post("/console/ins/add", e)
    }, e.destroy = function(e) {
        return t.post("/console/ins/delete", e)
    }, e.update = function(e) {
        return t.post("/console/ins/update", e)
    }, e
}]), angular.module("HostsControllers", ["ui.select", "ui.ace", "jsTree.directive"]).controller("HostsCtrl", ["$scope", "$state", function(t, e) {
    t.toDetail = function(t, a) {
        var o = a.node.data;
        if ("host" === o.node_type) return void e.go("hosts.hostDetail", {
            hostId: o.id
        });
        if ("project_module" === o.node_type) {
            if (0 === a.node.children.length) return;
            return void e.go("hosts.modules", {
                nodeId: o.id
            })
        }
    }, t.setDefaultNode = function(t, a) {
        e.is("hosts.hostDetail") ? a.instance.select_node("host-" + e.params.hostId, !0, !1) : e.is("hosts.modules") && a.instance.select_node("project_module-" + e.params.nodeId, !0, !1)
    }
}]).controller("HostsHostDetailCtrl", ["$scope", "$stateParams", "$http", "Host", function(t, e, a, o) {
    t.notManage = !1, t.loadStatus = {
        host: !1
    }, o.get({
        hostId: e.hostId
    }, function(e) {
        t.loadStatus.host = !0, t.host = e
    }), a.get("/deploy/api/can_manage_host", {
        params: {
            host_ids: e.hostId
        }
    }).success(function(a) {
        t.notManage = !a.result[e.hostId]
    })
}]).controller("HostsSoftDetailCtrl", ["$scope", "$stateParams", "$modal", "SoftDetail", function(t, e, a, o) {
    t.SoftDetails = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var s = {},
        l = function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.SoftDetails = e
        };
    t.pageChanged = function() {
        s.page = t.pagingOptions.currentPage, o.query(s, l)
    }, t.pageChanged()
}]).controller("HostsNewDeployCtrl", ["$scope", "$state", "$stateParams", "Host", "Soft", function(t, e, a, o, s) {
    t.host = {}, t.loadStatus = {
        host: !1,
        soft: !1,
        saving: !1
    }, o.query({
        host_ids: a.hostIds
    }, function(e) {
        t.host = e[0], t.host.ips = jQuery.map(e, function(t) {
            return t.ip
        }).join(","), t.hosts = e, t.loadStatus.host = !0
    }), t.salt_states = [], s.query(function(e) {
        t.salt_states = e, t.loadStatus.soft = !0
    }), t.submitNewDelpoy = function() {
        t.loadStatus.saving = !0, o.deploy({
            host_ids: a.hostIds,
            salt_state_ids: t.host.salt_state_ids
        }, function() {
            t.loadStatus.saving = !1, e.go("hosts.hostSaltJobList")
        })
    }
}]).controller("HostSaltJobListCtrl", ["$scope", "$stateParams", "$modal", "HostSaltJob", "HostSaltJobUtils", function(t, e, a, o, s) {
    t.hostSaltJobs = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var l = {
        host: "",
        host__ip: "",
        salt_job__sys_user__username__icontains: ""
    };
    t.queryParams = l, e.hostId && (l.host = e.hostId);
    var r = function(e, a) {
        t.pagingOptions.totalItems = a()["x-count"], t.hostSaltJobs = e;
        var o = 0,
            l = !1;
        jQuery.each(e, function() {
            this.bg_class = s.getBgClass(this), o++, o <= t.pagingOptions.perPage && 0 === this.status && !l && (setTimeout(t.pageChanged, 5e3), l = !0)
        })
    };
    t.pageChanged = function() {
        console.log(l), l.page = t.pagingOptions.currentPage, o.query(l, r)
    }, t.pageChanged(), t.viewJobResult = function(t) {
        a.open({
            templateUrl: "hosts/jobResultDetail.html",
            controller: ["$scope", "$modalInstance", function(e, a) {
                e.content = "", o.get({
                    hostSaltJobId: t
                }, function(t) {
                    e.content = JSON.stringify(JSON.parse(t.result_data), null, 4)
                }), e.ok = function() {
                    a.close()
                }
            }]
        })
    }
}]).controller("HostsEditFileCtrl", ["$scope", "$state", "$stateParams", "Host", function(t, e, a, o) {
    t.showFileDiff = !1, t.loadStatus = {
        host: !1,
        reading: !1,
        updating: !1
    }, t.showFileDiffText = "查看差异", t.fileresult = {
        total_count: 0,
        fail_count: 0,
        version_number: 0
    }, t.shellAceOption = {
        theme: "github",
        mode: "sh"
    }, t.fileAceOption = {
        theme: "github",
        mode: "text"
    }, t.fileDiffAceOption = {
        theme: "github",
        mode: "diff",
        showGutter: !1
    }, t.fileAceModel = "#请先填入文件路径,再点读取,稍等几秒即会加载你要编辑的文件的内容", t.preShellAceModel = '#!/usr/bin/env bash\necho "pre shell script"', t.postShellAceModel = '#!/usr/bin/env bash\necho "post shell script"', t.fileDiff = "", t.host = {}, o.query({
        host_ids: a.hostIds
    }, function(e) {
        t.host = e[0], t.host.ips = jQuery.map(e, function(t) {
            return t.ip
        }).join(","), t.hosts = e, t.loadStatus.host = !0
    }), t.enterReadfile = function(e) {
        13 === e.which && t.readHostFile()
    }, t.readHostFile = function() {
        window.confirm("确认读取吗?") && (t.loadStatus.reading = !0, o.readHostFile({
            file_path: t.host.file_path,
            host_ids: a.hostIds
        }, function(e) {
            t.loadStatus.reading = !1, t.fileAceModel = e.content, t.fileDiff = e.diff_result, angular.extend(t.fileresult, e)
        }))
    }, t.toggleShowDiff = function() {
        t.showFileDiff = !t.showFileDiff, t.showFileDiffText = t.showFileDiff ? "隐藏差异" : "查看差异"
    }, t.deployHostFile = function() {
        window.confirm("确认部署吗?") && (t.loadStatus.updating = !0, o.deployHostFile({
            file_path: t.host.file_path,
            host_ids: a.hostIds,
            new_file_content: t.fileAceModel,
            pre_script_content: t.preShellAceModel,
            post_script_content: t.postShellAceModel
        }, function() {
            t.loadStatus.updating = !1, e.go("hosts.hostSaltJobList")
        }))
    }
}]).controller("HostsModulesCtrl", ["$scope", "$state", "$stateParams", "$http", "Host", function(t, e, a, o, s) {
    t.selectHostIds = {}, t.noSelectHosts = !0, t.hostIds = [], t.hostAuths = {}, t.$watchCollection("selectHostIds", function() {
        if (t.hostIds = [], angular.forEach(t.selectHostIds, function(e, a) {
                e && t.hostIds.push(a)
            }), t.hostIds.length > 0) {
            for (var e = 0; e < t.hostIds.length; e++)
                if (!t.hostAuths[t.hostIds[e]]) return void(t.noSelectHosts = !0);
            t.noSelectHosts = !1
        } else t.noSelectHosts = !0
    }), s.query({
        project_module: a.nodeId
    }, function(e) {
        t.hosts = e, o.get("/deploy/api/can_manage_host", {
            params: {
                host_ids: jQuery.map(e, function(t) {
                    return t.id
                }).join(",")
            }
        }).success(function(e) {
            t.hostAuths = e.result
        })
    }), t.deploy = function() {
        e.go("hosts.deploy", {
            hostIds: t.hostIds.join(",")
        })
    }, t.editFile = function() {
        e.go("hosts.editFile", {
            hostIds: t.hostIds.join(",")
        })
    }, t.initEnv = function() {
        e.go("hosts.initEnv", {
            hostIds: t.hostIds.join(",")
        })
    }
}]).controller("HostsInitEnvCtrl", ["$scope", "$state", "$stateParams", "Host", function(t, e, a, o) {
    t.loadStatus = {
        host: !1,
        updating: !1
    }, o.query({
        host_ids: a.hostIds
    }, function(e) {
        t.loadStatus.host = !0, t.ips = jQuery.map(e, function(t) {
            return t.ip
        }).join(",")
    }), t.initEnv = function() {
        t.loadStatus.updating = !0, o.initEnv({
            host_ids: a.hostIds
        }, function() {
            t.loadStatus.updating = !1, e.go("hosts.hostSaltJobList")
        })
    }
}]), angular.module("UserSessionsControllers", []).controller("LoginStatusCtrl", ["$cookieStore", "$scope", "$http", function(t, e, a) {
    e.user = void 0, a.get("/deploy/api/current_user_info").success(function(a) {
        e.user = a, t.put("userid", a.id), t.put("username", a.username)
    })
}]);
var roles = {
        0: "管理员",
        1: "开发者",
        2: "运维"
    },
    setProjectUserLogic = function(t, e) {
        t.datas = {}, t.datas.sysUsers = [], e.query(function(e) {
            t.datas.sysUsers = e
        }), t.datas.projectUsers = [], t.datas.projectUser = {}, t.removeProjectUser = function(e) {
            var a = _.findIndex(t.datas.projectUsers, {
                sys_user_id: e
            });
            t.datas.projectUsers.splice(a, 1)
        }, t.getRoleName = function(t) {
            return roles[t]
        }, t.addProjectUser = function() {
            var e = t.datas.projectUser;
            if (void 0 === e.sys_user_id || void 0 === e.role) return void window.alert("请选择用户和角色");
            var a = _.findWhere(t.datas.projectUsers, {
                sys_user_id: Number(e.sys_user_id)
            });
            void 0 === a && (a = {
                sys_user_id: Number(e.sys_user_id),
                role: e.role
            }, t.datas.projectUsers.push(a), a.username = _.findWhere(t.datas.sysUsers, {
                id: Number(e.sys_user_id)
            }).username), a.role = e.role
        }
    };
angular.module("ProjectsControllers", ["ui.select", "ngSanitize", "ui.ace", "jsTree.directive", "validation", "validation.rule"]).controller("SidebarCtrl", ["$scope", "$state", "Project", function(t, e) {
    t.projectId = e.params.projectId
}]).controller("ProjectIndexCtrl", ["$scope", "$state", "Project", function(t, e, a) {
    t.projects = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    }, t.groups = [], a.getGroups(function(e) {
        t.groups = e, t.groups.unshift(["", "ALL"])
    });
    var o = {
        name__icontains: "",
        group_id: ""
    };
    t.queryParams = o;
    var s = function(e, a) {
        t.pagingOptions.totalItems = a()["x-count"], t.projects = e
    };
    t.pageChanged = function() {
        o.page = t.pagingOptions.currentPage, a.query(o, s)
    }, t.pageChanged(), t.projectDestroy = function(t) {
        window.confirm("确认删除吗?") && a.remove({
            projectId: t
        }, function() {
            e.go("projectIndex", {}, {
                reload: !0
            })
        })
    }
}]).controller("ProjectLogCtrl", ["$scope", "$state", "$modal", "HostSaltJob", "HostSaltJobUtils", "Project", "ProjectVersion", function(t, e, a, o, s, l, r) {
    t.hostSaltJobs = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    }, t.project = {}, l.get({
        projectId: e.params.projectId
    }, function(e) {
        t.project = e
    });
    var i = {
            project_id: e.params.projectId
        },
        n = function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.hostSaltJobs = e;
            var o = 0,
                l = !1;
            jQuery.each(e, function() {
                this.bg_class = s.getBgClass(this), o++, o <= t.pagingOptions.perPage && 0 === this.status && !l && (setTimeout(t.pageChanged, 5e3), l = !0)
            })
        };
    t.pageChanged = function() {
        i.page = t.pagingOptions.currentPage, o.project_jobs(i, n)
    }, t.pageChanged(), t.projectId = e.params.projectId, t.LogDetail = function(t, e) {
        a.open({
            templateUrl: "projects/logdetail.html",
            controller: ["$scope", "$modalInstance", function(a, o) {
                a.projectVersion = {}, a.project = {}, r.get({
                    projectVersionId: e
                }, function(t) {
                    a.projectVersion = t
                }), l.get({
                    projectId: t
                }, function(t) {
                    a.project = t
                }), a.ok = function() {
                    o.close()
                }
            }]
        })
    }
}]).controller("ProjectNewCtrl", ["$scope", "$state", "Project", "ProjectUtils", "SysUser", function(t, e, a, o, s) {
    t.loadStatus = {
        saving: !1
    }, t.project = {
        build_script: {
            content: ""
        },
        startVer: "",
        env: {}
    }, t.shAceOption = o.shAceOption;
    var l = {
        0: {
            build: 'echo "java build"\nmvn assembly:assembly',
            start: 'echo "java start"',
            stop: 'echo "java stop"'
        },
        1: {
            build: 'echo "python build"\npip install -r requirements.txt -i http://cloud.hunantv.com:6060/simple/',
            start: 'echo "python start"\n',
            stop: 'echo "python stop"'
        },
        2: {
            build: 'echo "php build"',
            start: 'echo "php start"',
            stop: 'echo "php stop"'
        },
        3: {
            build: "sh build.sh",
            start: 'echo "c start"',
            stop: 'echo "c stop"'
        },
        4: {
            build: "go build -a -o guard",
            start: 'echo "go start"',
            stop: 'echo "go stop"'
        }
    };
    t.changeLang = function() {
        if (!t.scriptIsChanged || window.confirm("脚本已被改动,是否用模板覆盖?")) {
            t.scriptIsChanged = !1;
            var e = l[t.project.lang];
            t.project.build_script.content = e.build
        }
    }, t.scriptChange = function() {
        t.scriptIsChanged = !0
    }, t.groups = [], a.getGroups(function(e) {
        t.groups = e
    }), t.projectNewSave = function() {
        var s = new a(t.project);
        t.loadStatus.saving = !0;
        s.$save(function(a) {
            t.loadStatus.saving = !1, e.go("sidebar.projectShow", {
                projectId: a.id
            })
        }, function() {
            t.loadStatus.saving = !1
        })
    }, t.openTree = function(t, e) {
        o.expandTree(e)
    }, t.hostCat = {
        treeInstance: null,
        selectedHosts: [],
        hosts: []
    }, t.selectTree = o.handleSelectTree(t), t.addHost = o.addHostToEnv, t.removeHost = o.removeHost, setProjectUserLogic(t, s)
}]).controller("ProjectShowCtrl", ["$scope", "$state", "Project", function(t, e, a) {
    t.project = {}, t.loadStatus = {
        project: !1
    }, a.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    })
}]).controller("ProjectEditCtrl", ["$scope", "$state", "Project", "ProjectUtils", "SysUser", function(t, e, a, o, s) {
    t.loadStatus = {
        project: !1,
        updating: !1
    }, t.editPage = !0, t.project = {
        project_hosts: []
    }, t.shAceOption = o.shAceOption, t.groups = [], a.getGroups(function(e) {
        t.groups = e
    }), t.openTree = function(t, e) {
        o.expandTree(e)
    }, t.hostCat = {
        treeInstance: null,
        selectedHosts: [],
        hosts: []
    }, t.selectTree = o.handleSelectTree(t), t.addHost = o.addHostToEnv, t.removeHost = o.removeHost, a.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e, t.hostCat.hosts = jQuery.map(e.project_hosts, function(t) {
            return {
                id: t.host_id,
                ip: t.host_ip,
                isProd: t.is_prod_env
            }
        }), t.project.startVer = e.start_ver.name, _.each(e.project_user_list, function(e) {
            t.datas.projectUsers.push({
                sys_user_id: e.sys_user_id,
                username: e.username,
                role: String(e.role)
            })
        })
    }), t.projectUpdateSave = function() {
        t.loadStatus.updating = !0, t.project.hosts = t.hostCat.hosts, t.project.project_users = t.datas.projectUsers, console.log(t.project), a.update({
            projectId: t.project.id
        }, t.project, function(a) {
            t.loadStatus.updating = !1, e.go("sidebar.projectShow", {
                projectId: a.id
            })
        })
    }, setProjectUserLogic(t, s)
}]), angular.module("ProjectVersionsControllers", ["ui.select", "ngSanitize", "ui.ace", "validation", "validation.rule", "checklist-model", "dndLists"]).controller("ProjectVersionNewCtrl", ["$scope", "$state", "Project", "ProjectVersion", function(t, e, a, o) {
    t.projectId = e.params.projectId, t.refs = [], t.projectVersion = {}, t.project = {}, t.baseImage = {}, t.loadStatus = {
        project: !1,
        git: !1,
        ver: !1,
        saving: !1
    }, t.setSelectedRef = function(e) {
        t.selectedRef = e;
        t.projectVersion.ref_name = e.name;
        t.projectVersion.message = e.message;
    }, t.setSelectedBaseImage = function(e) {
        t.baseImageName = e;
    }, t.setSelectedPod = function(e) {
        t.pod = e;
    }, t.projectVersionNewSave = function() {
        t.loadStatus.saving = !0;
        t.projectVersion.project_id = t.projectId;
        var s = new o(t.projectVersion);
        s.$save(function(build_id) {
            t.loadStatus.saving = !1, e.go("sidebar.projectVersionIndex", {
                projectId: t.projectId
            })
        })
    }, a.gitRefs({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.git = !0, t.refs = e
    });
    a.baseImages({}, function(e) {
        t.baseImageNames = e;
    });
    a.getPods({}, function(e) {
        t.pods = e;
    });
    a.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    })
}]).controller("ProjectVersionIndexCtrl", ["$scope", "$state", "Project", "ProjectVersion", function(t, e, a, o) {
    t.projectId = e.params.projectId, t.projectVersions = [], t.project = {}, a.get({
        projectId: e.params.projectId
    }, function(e) {
        t.project = e
    }), t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var s = {
            project_id: e.params.projectId
        },
        l = function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.projectVersions = e
        };
    t.pageChanged = function() {
        s.page = t.pagingOptions.currentPage, o.query(s, l)
    }, t.pageChanged()
}]).controller("ProjectVersionShowCtrl", ["$scope", "$http", "$state", "$modal", "Project", "ProjectVersion", function(t, e, a, o, s, l) {
    t.loadStatus = {
        projectVersion: !1,
        deploy: !1,
        rollback: !1,
        retryApiTest: !1
    }, t.projectId = a.params.projectId, t.projectVersion = {}, t.project = {};
    var r = function() {
        l.get({
            projectVersionId: a.params.projectVersionId
        }, function(e) {
            t.loadStatus.projectVersion = !0, t.projectVersion = e, 0 === e.status && setTimeout(r, 5e3)
        })
    };
    r(), s.get({
        projectId: a.params.projectId
    }, function(e) {
        t.project = e
    }), t.retryApiTest = function() {
        t.loadStatus.retryApiTest = !0, l.retryApiTest({
            projectVersionId: a.params.projectVersionId
        }, {}, function() {
            a.go("sidebar.projectVersionShow", {
                projectId: t.projectId,
                projectVersionId: a.params.projectVersionId
            })
        })
    }, t.showBuildOutput = function() {
        o.open({
            templateUrl: "projectVersions/buildOutput.html",
            controller: ["$scope", "$modalInstance", function(e, a) {
                e.content = "", e.content = t.projectVersion.build_output, e.ok = function() {
                    a.close()
                }
            }]
        })
    }, t.drawing = {
        projectNew: {
            enable: !1,
            className: "success"
        },
        projectBuild: {
            enable: !1,
            className: "success"
        },
        projectAutoTest: {
            enable: !1,
            className: "success"
        },
        projectFuncTest: {
            enable: !1,
            className: "success"
        },
        projectApply: {
            enable: !1,
            className: "success"
        },
        projectDeploy: {
            enable: !1,
            className: "success"
        }
    }, l.drawing({
        projectVersionId: a.params.projectVersionId
    }, function(e) {
        t.drawing = e
    })
}]), angular.module("OperationRecordsControllers", ["ngSanitize"]).controller("OperationRecordIndexCtrl", ["$scope", "$stateParams", "$modal", "OperationRecord", function(t, e, a, o) {
    t.operationRecords = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var s = {};
    t.pageChanged = function() {
        s.page = t.pagingOptions.currentPage, o.query(s, function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.operationRecords = e
        })
    }, t.pageChanged(), t.viewResult = function(t) {
        a.open({
            templateUrl: "hosts/jobResultDetail.html",
            controller: ["$scope", "$modalInstance", function(e, a) {
                e.content = JSON.stringify(JSON.parse(t.ext_info), null, 4), e.ok = function() {
                    a.close()
                }
            }]
        })
    }
}]).controller("OperationRecordReportCtrl", ["$scope", "OperationRecord", function(t, e) {
    t.queryParams = {
        start_date: moment().day(1).format("YYYY-MM-DD"),
        end_date: moment().day(8).format("YYYY-MM-DD")
    }, t.reportAll = {}, t.reportProject = [], t.reportUser = [], t.queryAll = function() {
        e.queryAll(t.queryParams, function(e) {
            t.reportAll = e
        })
    }, t.queryProject = function() {
        e.queryProject(t.queryParams, function(e) {
            t.reportProject = e
        })
    }, t.queryUser = function() {
        e.queryUser(t.queryParams, function(e) {
            t.reportUser = e
        })
    }
}]), angular.module("ApprovalSheetTemplatesControllers", ["ngSanitize"]).controller("ApprovalSheetTemplateIndexCtrl", ["$scope", "$state", "ApprovalSheetTemplate", "Project", function(t, e, a, o) {
    t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.project = e
    }), t.approvalSheetTemplates = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var s = {
            project_id: e.params.projectId
        },
        l = function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.approvalSheetTemplates = e
        };
    t.pageChanged = function() {
        s.page = t.pagingOptions.currentPage, a.query(s, l)
    }, t.pageChanged(), t.approvalSheetTemplateDelete = function(t) {
        window.confirm("确认删除吗?") && a.remove({
            approvalSheetTemplateId: t
        }, function() {
            e.go("sidebar.approvalSheetTemplateIndex", {
                projectId: e.params.projectId
            }, {
                reload: !0
            })
        })
    }
}]).controller("ApprovalSheetTemplateShowCtrl", ["$scope", "$state", "ApprovalSheetTemplate", "Project", function(t, e, a, o) {
    t.loadStatus = {
        project: !1,
        approvalSheetTemplate: !1
    }, t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    }), t.approvalSheetTemplate = {}, a.get({
        approvalSheetTemplateId: e.params.approvalSheetTemplateId
    }, function(e) {
        t.loadStatus.approvalSheetTemplate = !0, t.approvalSheetTemplate = e
    })
}]).controller("ApprovalSheetTemplateNewCtrl", ["$scope", "$state", "ApprovalSheetTemplate", "Project", "ProjectUtils", function(t, e, a, o, s) {
    t.loadStatus = {
        project: !1,
        saving: !1
    }, t.editPage = !1, t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    }), t.shAceOption = s.shAceOption, t.radioValues = {
        T: !0,
        F: !1
    }, t.approvalSheetTemplate = {
        start_script: {},
        stop_script: {},
        is_prod_env: !1
    }, t.approvalSheetTemplateNewSave = function() {
        t.loadStatus.saving = !0, t.approvalSheetTemplate.project_id = e.params.projectId;
        var o = new a(t.approvalSheetTemplate);
        o.$save(function(a) {
            t.loadStatus.saving = !1, e.go("sidebar.approvalSheetTemplateShow", {
                approvalSheetTemplateId: a.id,
                projectId: t.projectId
            })
        })
    }
}]).controller("ApprovalSheetTemplateEditCtrl", ["$scope", "$state", "ApprovalSheetTemplate", "Project", "ProjectUtils", function(t, e, a, o, s) {
    t.loadStatus = {
        project: !1,
        approvalSheetTemplate: !1,
        saving: !1
    }, t.editPage = !0, t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    }), t.shAceOption = s.shAceOption, t.radioValues = {
        T: !0,
        F: !1
    }, t.approvalSheetTemplate = {
        start_script: {},
        stop_script: {},
        is_prod_env: !1
    }, a.get({
        approvalSheetTemplateId: e.params.approvalSheetTemplateId
    }, function(e) {
        t.loadStatus.approvalSheetTemplate = !0, t.approvalSheetTemplate = e
    }), t.approvalSheetTemplateEditSave = function() {
        t.loadStatus.saving = !0, t.approvalSheetTemplate.project_id = e.params.projectId, a.update({
            approvalSheetTemplateId: e.params.approvalSheetTemplateId
        }, t.approvalSheetTemplate, function(a) {
            t.loadStatus.saving = !1, e.go("sidebar.approvalSheetTemplateShow", {
                approvalSheetTemplateId: a.id,
                projectId: t.projectId
            })
        })
    }
}]), angular.module("ApprovalSheetsControllers", ["ngSanitize"]).controller("ApprovalSheetNewCtrl", ["$scope", "$state", "ApprovalSheet", "Project", "ProjectUtils", "ProjectVersion", "ApprovalSheetTemplate", function(t, e, a, o, s, l, r) {
    t.loadStatus = {
        project: !1,
        projectVersions: !1,
        approvalSheetTemplates: !1,
        saving: !1
    }, t.datas = {
        hosts: []
    }, t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e, t.projectHostMap = {}, _.each(e.project_hosts, function(e) {
            var a = e.host_module + " / " + e.host_project + " / " + e.host_env,
                o = t.projectHostMap[a];
            void 0 === o && (t.projectHostMap[a] = [], o = t.projectHostMap[a]), o.push(e)
        })
    }), t.projectVersions = [], l.query({
        project_id: e.params.projectId,
        status: 1
    }, function(e) {
        t.loadStatus.projectVersions = !0, t.projectVersions = e
    }), t.approvalSheetTemplates = [], r.query({
        project_id: e.params.projectId
    }, function(e) {
        t.loadStatus.approvalSheetTemplates = !0, t.approvalSheetTemplates = e
    }), t.successSheets = [], a.query({
        project_version__project_id: e.params.projectId,
        status: "4,5"
    }, function(e) {
        t.successSheets = e
    }), t.approvalSheet = {}, t.approvalSheetNewSave = function() {
        t.approvalSheet.hosts = _.uniq(t.datas.hosts, _.iteratee("host_id")), _.each(t.approvalSheet.hosts, function(t, e) {
            t.position = e + 1
        });
        var o = new a(t.approvalSheet);
        o.$save(function(t) {
            e.go("sidebar.approvalSheetShow", {
                approvalSheetId: t.id,
                projectId: e.params.projectId
            })
        })
    }, t.changeTemplate = function() {
        jQuery.each(t.approvalSheetTemplates, function(e, a) {
            return a.id === t.approvalSheet.approval_sheet_template_id ? (t.datas.start_script = a.start_script.content, t.datas.stop_script = a.stop_script.content, !1) : void 0
        })
    }, t.addHost = function() {
        var e = arguments[0],
            a = arguments[1];
        if (e.enabled = void 0 === a ? !e.enabled : a, e.enabled) e.break_point = !1, t.datas.hosts.push(e);
        else {
            var o = _.findIndex(t.datas.hosts, {
                host_id: e.host_id
            });
            t.datas.hosts.splice(o, 1)
        }
    };
    var i = {};
    t.selectNode = function(e) {
        var a = t.projectHostMap[e];
        i[e] = !i[e], _.each(a, function(a) {
            t.addHost(a, i[e])
        })
    }
}]).controller("ApprovalSheetShowCtrl", ["$scope", "$state", "ApprovalSheet", "Project", function(t, e, a, o) {
    t.loadStatus = {
        project: !1,
        approvalSheet: !1
    }, t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.loadStatus.project = !0, t.project = e
    }), t.approvalSheet = {
        can_deploy: !1,
        can_rollback: !1
    }, a.get({
        approvalSheetId: e.params.approvalSheetId
    }, function(e) {
        t.loadStatus.approvalSheet = !0, t.approvalSheet = e
    }), t.auditSheet = function(t) {
        a.audit({
            approvalSheetId: e.params.approvalSheetId
        }, {
            approval_status: t
        }, function(t) {
            e.go("sidebar.approvalSheetShow", {
                approvalSheetId: t.id,
                projectId: e.params.projectId
            }, {
                reload: !0
            })
        })
    }, t.deploy = function() {
        a.deploy({
            approvalSheetId: e.params.approvalSheetId
        }, {}, function() {
            e.go("sidebar.projectLog", {
                projectId: e.params.projectId
            }, {
                reload: !0
            })
        })
    }, t.rollback = function() {
        a.rollback({
            approvalSheetId: e.params.approvalSheetId
        }, {}, function() {
            e.go("sidebar.projectLog", {
                projectId: e.params.projectId
            }, {
                reload: !0
            })
        })
    }
}]).controller("ApprovalSheetIndexCtrl", ["$scope", "$state", "ApprovalSheet", "Project", function(t, e, a, o) {
    t.projectId = e.params.projectId, t.project = {}, o.get({
        projectId: e.params.projectId
    }, function(e) {
        t.project = e
    }), t.approvalSheets = [], t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var s = {
            project_version__project_id: e.params.projectId
        },
        l = function(e, a) {
            t.pagingOptions.totalItems = a()["x-count"], t.approvalSheets = e
        };
    t.pageChanged = function() {
        s.page = t.pagingOptions.currentPage, a.query(s, l)
    }, t.pageChanged()
}]), angular.module("ProjectAppsControllers", ["ngSanitize"]).controller("ProjectAppIndexCtrl", ["$scope", "$state", "$cookieStore", "$window", "$modal", "ProjectApp", function(t, e, a, o, s, l) {
    t.datas = {
        projectApps: []
    }, t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var r = {
            apply_user: a.get("username")
        },
        i = function(e) {
            t.pagingOptions.totalItems = e.data.count, t.datas.projectApps = e.data.info, t.datas.domains = e.data.domain, t.datas.configs = e.data.config
        };
    t.pageChanged = function() {
        r.pn = t.pagingOptions.currentPage, r.size = t.pagingOptions.perPage, l.list(r).then(i)
    }, t.pageChanged(), t.deploy = function(t) {
        window.confirm("确认部署吗?") && l.deploy({
            appid: t,
            userid: a.get("userid")
        }).then(function() {
            e.go("projectAppIndex", {}, {
                reload: !0
            }), o.alert("部署成功")
        })
    }, t.destroy = function(t) {
        window.confirm("确认删除吗?") && l.destroy({
            appid: t,
            userid: a.get("userid")
        }).then(function() {
            e.go("projectAppIndex", {}, {
                reload: !0
            }), o.alert("删除成功")
        })
    }, t.updateRouter = function(t) {
        window.confirm("确认更新路由吗?") && l.updateRouter({
            appid: t
        }).then(function() {
            e.go("projectAppIndex", {}, {
                reload: !0
            }), o.alert("更新路由成功")
        })
    }, t.openEdit = function(e) {
        s.open({
            templateUrl: "projectApps/edit.html",
            controller: "ProjectAppEditCtrl",
            size: "lg",
            resolve: {
                appinfo: function() {
                    var a = _.findWhere(t.datas.configs, {
                        appid: e.appid
                    });
                    return a = _.pick(a, "appid", "container_type", "max", "min")
                }
            }
        })
    }, t.openShow = function(t) {
        s.open({
            templateUrl: "projectApps/show.html",
            controller: "ProjectAppShowCtrl",
            size: "lg",
            resolve: {
                appinfo: function() {
                    return t
                }
            }
        })
    };
    var n = {
        k0: "初始化中",
        k1: "可用"
    };
    t.statusName = function(t) {
        return n["k" + t]
    }
}]).controller("ProjectAppNewCtrl", ["$cookieStore", "$window", "$scope", "$state", "ProjectApp", function(t, e, a, o, s) {
    a.datas = {
        options: {}
    }, a.projectApp = {}, s.options().then(function(t) {
        a.datas.options = t.data
    }), a.createProjectApp = function() {
        a.projectApp.apply_user = t.get("username"), a.projectApp.userid = t.get("userid"), s.create(a.projectApp).then(function() {
            o.go("projectAppIndex"), e.alert("创建成功")
        })
    }
}]).controller("ProjectAppEditCtrl", ["$scope", "$state", "$modalInstance", "$window", "ProjectApp", "appinfo", function(t, e, a, o, s, l) {
    t.datas = {
        options: {}
    }, t.projectApp = l, t.projectApp.container_type = String(l.container_type), s.options().then(function(e) {
        t.datas.options = e.data
    }), t.updateApp = function() {
        s.update(t.projectApp).then(function() {
            a.dismiss("cancel"), e.go("projectAppIndex", {}, {
                reload: !0
            }), o.alert("更新成功")
        })
    }, t.cancel = function() {
        a.dismiss("cancel")
    }
}]).controller("ProjectAppShowCtrl", ["$scope", "$state", "$modalInstance", "$window", "appinfo", function(t, e, a, o, s) {
    t.projectApp = s, t.cancel = function() {
        a.dismiss("cancel")
    }
}]).controller("AppLogIndexCtrl", ["$scope", "$state", "ProjectApp", function(t, e, a) {
    t.datas = {
        appLogs: []
    }, t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var o = {},
        s = function(e) {
            t.pagingOptions.totalItems = e.data.count, t.datas.appLogs = e.data.info
        };
    t.pageChanged = function() {
        o.pn = t.pagingOptions.currentPage, o.size = t.pagingOptions.perPage, a.logList(o).then(s)
    }, t.pageChanged()
}]).controller("AppDomainNewCtrl", ["$scope", "$state", "$cookieStore", "$window", "ProjectApp", function(t, e, a, o, s) {
    t.appid = e.params.appid, t.appDomain = {}, t.createAppDomain = function() {
        t.appDomain.apply_user = a.get("username"), t.appDomain.appid = t.appid, s.createAppDomain(t.appDomain).then(function() {
            e.go("appDomainIndex", {
                appid: t.appid
            }), o.alert("创建成功")
        })
    }
}]).controller("AppDomainIndexCtrl", ["$scope", "$state", "$cookieStore", "$window", "ProjectApp", function(t, e, a, o, s) {
    t.appid = e.params.appid, t.appDomains = [], s.listAppDomain({
        appid: t.appid
    }).then(function(e) {
        t.appDomains = e.data
    }), t.destroy = function(l) {
        window.confirm("确认删除吗?") && s.destroyAppDomain({
            id: l,
            appid: t.appid,
            userid: a.get("userid")
        }).then(function() {
            e.go("appDomainIndex", {
                appid: t.appid
            }, {
                reload: !0
            }), o.alert("删除成功")
        })
    }
}]), angular.module("AppVersionsControllers", ["ngSanitize"]).controller("AppVersionIndexCtrl", ["$scope", "$state", "$window", "$cookieStore", "AppVersion", function(t, e, a, o, s) {
    t.appid = e.params.appid, t.datas = {
        appVersions: []
    }, t.setAsCurrent = function(l) {
        window.confirm("确认设为当前版本吗?") && s.setAsCurrent({
            version: l,
            userid: o.get("userid"),
            appid: t.appid
        }).then(function() {
            e.go("appVersionIndex", {
                appid: t.appid
            }, {
                reload: !0
            }), a.alert("设置成功")
        })
    }, t.manualBuild = function(o) {
        window.confirm("确认手动构建吗?") && s.manualBuild({
            version: o,
            appid: t.appid
        }).then(function() {
            a.alert("构建中"), e.go("appVersionIndex", {
                appid: t.appid
            }, {
                reload: !0
            })
        })
    }, t.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var l = {
            appid: t.appid
        },
        r = function(e) {
            t.pagingOptions.totalItems = e.data.count, t.datas.appVersions = e.data
        };
    t.pageChanged = function() {
        l.pn = t.pagingOptions.currentPage, l.size = t.pagingOptions.perPage, s.list(l).then(r)
    }, t.pageChanged();
    var i = {
        "k-1": "构建中",
        k0: "未构建",
        k1: "构建完成"
    };
    t.statusName = function(t) {
        return i["k" + t]
    }
}]).controller("AppVersionNewCtrl", ["$scope", "$state", "$window", "$cookieStore", "AppVersion", "ProjectApp", function(t, e, a, o, s, l) {
    t.appid = e.params.appid, t.appVersion = {}, t.datas = {
        gitRefs: [],
        currentGitRef: {}
    }, l.gitRefs(t.appid).then(function(e) {
        t.datas.gitRefs = e.data
    }), t.changeGitRefs = function() {
        t.datas.currentGitRef = _.findWhere(t.datas.gitRefs, {
            hexsha: t.appVersion.git_version
        })
    }, t.createAppVersion = function() {
        t.appVersion.appid = e.params.appid, t.appVersion.userid = o.get("userid"), s.create(t.appVersion).then(function() {
            e.go("appVersionIndex", {
                appid: t.appid
            }), a.alert("创建成功")
        })
    }
}]), angular.module("AppInstancesControllers", ["ngSanitize"]).controller("AppInstanceIndexCtrl", ["$modal", "$window", "$cookieStore", "$scope", "$state", "AppInstance", function(t, e, a, o, s, l) {
    o.appid = s.params.appid, o.datas = {
        appInstances: []
    }, o.pagingOptions = {
        currentPage: 1,
        totalItems: 0,
        perPage: 20
    };
    var r = {
            appid: o.appid
        },
        i = function(t) {
            o.pagingOptions.totalItems = t.data.count, o.datas.appInstances = t.data
        };
    o.pageChanged = function() {
        r.pn = o.pagingOptions.currentPage, r.size = o.pagingOptions.perPage, l.list(r).then(i)
    }, o.pageChanged(), o.destroy = function(t) {
        window.confirm("确认删除吗?") && l.destroy({
            appid: o.appid,
            userid: a.get("userid"),
            ins_id: t
        }).then(function() {
            s.go("appInstanceIndex", {
                appid: o.appid
            }, {
                reload: !0
            }), e.alert("删除成功")
        })
    }, o.openGrayDeploy = function(e) {
        t.open({
            templateUrl: "appInstances/grayDeploy.html",
            controller: "AppInstanceGrayDeployCtrl",
            size: "lg",
            resolve: {
                appinfo: function() {
                    return {
                        appid: o.appid,
                        ins_id: e
                    }
                }
            }
        })
    };
    var n = {
        k0: "初始化中",
        k1: "运行中"
    };
    o.statusName = function(t) {
        return n["k" + t]
    }, o.appInstanceNew = function() {
        o.appInstance = {}, o.appInstance.appid = o.appid, o.appInstance.userid = a.get("userid"), l.create(o.appInstance).then(function() {
            s.go("appInstanceIndex", {
                appid: o.appid
            }, {
                reload: !0
            }), e.alert("创建成功")
        })
    }
}]).controller("AppInstanceGrayDeployCtrl", ["$scope", "$state", "$modalInstance", "$window", "AppVersion", "AppInstance", "appinfo", function(t, e, a, o, s, l, r) {
    t.appid = r.appid, t.appInstance = _.pick(r, "appid", "ins_id"), t.datas = {
        appVersions: [],
        version: null
    }, s.list({
        appid: t.appid
    }).then(function(e) {
        t.datas.appVersions = e.data
    }), t.grayDeploy = function() {
        window.confirm("确认灰度吗?") && (t.appInstance.version = t.datas.version.version, l.update(t.appInstance).then(function() {
            e.go("appInstanceIndex", {
                appid: t.appid
            }, {
                reload: !0
            }), o.alert("灰度部署成功")
        }), a.dismiss("cancel"))
    }, t.cancel = function() {
        a.dismiss("cancel")
    }
}]);
